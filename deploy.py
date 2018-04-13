#!/usr/bin/python

from json import load
from os import path
from pathlib import Path
from time import sleep
from zipfile import ZipFile

from boto3 import client, resource
import botocore

class Build():
    """Creates a build for AWS lambda deployment."""

    ROOT_PATH = path.dirname(path.abspath(__file__))

    def __init__(self):
        package_json = load(open(self.ROOT_PATH + '/package.json'))
        self.builds_directory = self.ROOT_PATH + '/builds/'
        self.version_number = package_json['version']
        self.app_code_filename = package_json['main']
        self.out_filename = self.version_number + '.zip'
        self.out_filepath = self.builds_directory + self.out_filename

    def version_exists(self, version):
        """Checks if the proposed build already exists in /builds."""
        return path.exists(self.out_filepath)

    def ensure_builds_directory(self):
        """Creates the /build directory if it does not exist."""
        return Path(self.builds_directory).mkdir(parents=False, exist_ok=True)

    def create_build(self):
        """Zips the current directory into the /builds directory."""
        self.ensure_builds_directory()

        if self.version_exists(self.version_number):
            print("\nFAILED\nBuild artifact already exists. Update package.json version before deploying.\n")
            return False
        else:
            # TODO: fix so that node_modules are formatted properly
            with ZipFile(self.out_filepath, 'w') as f:
                f.write(self.app_code_filename)
                f.write(self.ROOT_PATH + '/node_modules/')

        print("\nBuild successful!\n")
        return True

    def file_exists_on_s3(self, client):
        """Checks s3, confirms that the build does not already exist."""
        resp = client.list_objects_v2(
            Bucket='recipe-robot',
            Prefix=self.out_filename,
        )
        for obj in resp.get('Contents', []):
            if obj['Key'] == self.out_filename:
                return True

        return False

    def upload_to_s3(self):
        """Uploads the file to s3."""
        s3_client = client('s3')
        s3_resource = resource('s3')

        if self.file_exists_on_s3(s3_client):
            print("Build already exists on s3. Abandoning deploy.")
            return False

        data = open(self.out_filepath, 'rb')
        try:
            resp = s3_resource.Bucket('recipe-robot').put_object(Key=self.out_filename, Body=data)
        except s3_client.exceptions.NoSuchBucket as e:
            print("Bucket doesn't exist. Create it in the AWS console.\nYour buckets:")
            for bucket in s3_resource.buckets.all():
                print(bucket.name)
            return False

        return True

    def update_lambda_to_latest_build(self):
        """Update your lambda function with the latest build on s3."""
        lambda_client = client('lambda')

        resp = lambda_client.update_function_code(
            FunctionName='myRecipeRobot',
            Publish=True,
            S3Bucket='recipe-robot',
            S3Key=self.out_filename
        )

        if resp['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('\nUpdated s3 and lambda!\n')
            return True
        else:
            raise

    def deploy_latest(self):
        """Uploads the latest build to s3 and publishes it to lambda."""
        self.upload_to_s3()
        sleep(10)
        self.update_lambda_to_latest_build()

        return True

if __name__ == '__main__':
    b = Build()
    if b.create_build():
        b.deploy_latest()
