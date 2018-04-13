#!/usr/bin/python

import json
import os
import pathlib
from zipfile import ZipFile

import boto3

class Build():
    """Creates a build for AWS lambda deployment."""

    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        package_json = json.load(open(self.ROOT_PATH + '/package.json'))
        self.version_number = package_json['version']
        self.main_filename = package_json['main']

    def version_exists(self, version):
        return os.path.exists(self.ROOT_PATH + '/builds/' + version + '.zip')

    def ensure_builds_directory(self):
        pathlib.Path(self.ROOT_PATH + '/builds').mkdir(parents=False, exist_ok=True)

    def create_build(self):
        """Zips the current directory into the /builds directory."""
        self.ensure_builds_directory()

        # TODO: pull latest version number from S3 so we can check against what's live.
        if self.version_exists(self.version_number):
            print("\nFAILED\nBuild artifact already exists. Update package.json version before deploying.\n")
            return
        else:
            outfile_name = self.ROOT_PATH + '/builds/' + self.version_number + '.zip'
            with ZipFile(outfile_name, 'w') as f:
                f.write(self.main_filename)
                f.write(self.ROOT_PATH + '/node_modules/')

    # TODO: implement via boto
    def upload_to_s3(self):
        pass

    # TODO: update to pull from latest s3 once upload_to_s3 becomes necessary (> 10mb build file).
    def update_lambda_to_latest_build(self):
        # TODO: pull latest version number from S3, don't deploy if it already exists.
        pass

    def deploy_latest(self):
        # TODO: uncomment once upload_to_s3 is complete
        # self.upload_to_s3()
        self.update_lambda_to_latest_build()

if __name__ == '__main__':
    b = Build()
    b.create_build()
    b.deploy_latest()
