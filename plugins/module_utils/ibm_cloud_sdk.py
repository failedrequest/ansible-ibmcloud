#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

"""
IBM Cloud SDK utilities for Ansible modules.

This module provides authentication and common utilities for interacting
with IBM Cloud APIs using the native Python SDK.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
from typing import Optional, Dict, Any
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException


class IBMCloudAuth:
    """
    Handle IBM Cloud authentication using IAM API key.
    
    Supports multiple methods of providing credentials:
    1. Module parameters (ibmcloud_api_key)
    2. Environment variables (IC_API_KEY, IBMCLOUD_API_KEY)
    3. IBM Cloud CLI configuration
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize IBM Cloud authentication.
        
        Args:
            api_key: IBM Cloud API key. If not provided, will check environment variables.
        """
        self.api_key = api_key or self._get_api_key_from_env()
        if not self.api_key:
            raise ValueError(
                "IBM Cloud API key not found. Please provide via 'ibmcloud_api_key' "
                "parameter or set IC_API_KEY/IBMCLOUD_API_KEY environment variable."
            )
        
        self.authenticator = IAMAuthenticator(self.api_key)
    
    @staticmethod
    def _get_api_key_from_env() -> Optional[str]:
        """Get API key from environment variables."""
        return os.environ.get('IC_API_KEY') or os.environ.get('IBMCLOUD_API_KEY')
    
    def get_authenticator(self) -> IAMAuthenticator:
        """Return the IAM authenticator instance."""
        return self.authenticator


class IBMCloudSDKModule:
    """
    Base class for IBM Cloud SDK-based Ansible modules.
    
    Provides common functionality for all IBM Cloud modules including:
    - Authentication handling
    - Error handling and formatting
    - Common parameter validation
    - Result formatting
    """
    
    def __init__(self, module):
        """
        Initialize the IBM Cloud SDK module.
        
        Args:
            module: AnsibleModule instance
        """
        self.module = module
        self.params = module.params
        
        # Initialize authentication
        api_key = self.params.get('ibmcloud_api_key')
        try:
            self.auth = IBMCloudAuth(api_key)
        except ValueError as e:
            self.module.fail_json(msg=str(e))
        
        # Common parameters
        self.region = self.params.get('region', 'us-south')
        self.resource_group_id = self.params.get('resource_group')
        self.state = self.params.get('state', 'present')
        
        # Result dictionary
        self.result = {
            'changed': False,
            'resource': {},
            'msg': ''
        }
    
    def handle_api_exception(self, e: ApiException, operation: str = "operation") -> None:
        """
        Handle IBM Cloud API exceptions and fail with formatted message.
        
        Args:
            e: ApiException from IBM Cloud SDK
            operation: Description of the operation that failed
        """
        error_msg = f"Failed to {operation}: {str(e)}"
        
        if hasattr(e, 'message'):
            error_msg = f"Failed to {operation}: {e.message}"
        
        if hasattr(e, 'code'):
            error_msg += f" (Status code: {e.code})"
        
        # Remove msg from result to avoid duplicate parameter
        result_copy = {k: v for k, v in self.result.items() if k != 'msg'}
        self.module.fail_json(msg=error_msg, **result_copy)
    
    def exit_json(self, **kwargs):
        """Exit with JSON result."""
        self.result.update(kwargs)
        self.module.exit_json(**self.result)
    
    def fail_json(self, msg: str, **kwargs):
        """Exit with JSON failure."""
        self.result.update(kwargs)
        # Remove msg from result to avoid duplicate parameter
        result_copy = {k: v for k, v in self.result.items() if k != 'msg'}
        self.module.fail_json(msg=msg, **result_copy)
    
    @staticmethod
    def get_resource_id(resource: Dict[str, Any]) -> Optional[str]:
        """
        Extract resource ID from resource object.
        
        Args:
            resource: Resource dictionary from API response
            
        Returns:
            Resource ID or None
        """
        if isinstance(resource, dict):
            return resource.get('id') or resource.get('crn')
        return None
    
    @staticmethod
    def compare_resources(current: Dict[str, Any], desired: Dict[str, Any], 
                         ignore_keys: Optional[list] = None) -> bool:
        """
        Compare current and desired resource states.
        
        Args:
            current: Current resource state
            desired: Desired resource state
            ignore_keys: List of keys to ignore in comparison
            
        Returns:
            True if resources match, False otherwise
        """
        if ignore_keys is None:
            ignore_keys = ['id', 'crn', 'created_at', 'updated_at', 'href', 
                          'resource_group', 'status']
        
        for key, value in desired.items():
            if key in ignore_keys:
                continue
            
            if key not in current:
                return False
            
            if isinstance(value, dict):
                if not IBMCloudSDKModule.compare_resources(
                    current.get(key, {}), value, ignore_keys
                ):
                    return False
            elif isinstance(value, list):
                if len(current.get(key, [])) != len(value):
                    return False
            elif current.get(key) != value:
                return False
        
        return True
    
    def check_mode_exit(self, changed: bool = False, msg: str = ""):
        """Exit if running in check mode."""
        if self.module.check_mode:
            self.result['changed'] = changed
            if msg:
                self.result['msg'] = msg
            self.module.exit_json(**self.result)


def get_common_argument_spec() -> Dict[str, Any]:
    """
    Return common argument specification for IBM Cloud modules.
    
    Returns:
        Dictionary of common module arguments
    """
    return {
        'ibmcloud_api_key': {
            'type': 'str',
            'required': False,
            'no_log': True,
            'fallback': (os.environ.get, ['IC_API_KEY', 'IBMCLOUD_API_KEY'])
        },
        'region': {
            'type': 'str',
            'required': False,
            'default': 'us-south',
            'choices': [
                'us-south', 'us-east', 'eu-gb', 'eu-de', 'jp-tok', 
                'au-syd', 'jp-osa', 'ca-tor', 'br-sao'
            ]
        },
        'resource_group': {
            'type': 'str',
            'required': False
        },
        'state': {
            'type': 'str',
            'required': False,
            'default': 'present',
            'choices': ['present', 'absent']
        }
    }
