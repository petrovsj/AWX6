#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2023, Zscaler, Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_application_segment_browser_access_info
short_description: Retrieves browser access application segment information.
description:
  - This module will allow the retrieval of information about a browser access application segment.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
    - zscaler.zpacloud.fragments.credentials_set
    - zscaler.zpacloud.fragments.provider
options:
  name:
    description:
      - Name of the App Connector Group.
    required: false
    type: str
  id:
    description:
      - ID of the App Connector Group.
    required: false
    type: str
"""

EXAMPLES = """
- name: Gather information about all browser access application segments
  zscaler.zpacloud.zpa_application_segment_browser_access_info:
    provider: "{{ zpa_cloud }}"

- name: Browser Access Application Segment by Name
  zscaler.zpacloud.zpa_application_segment_browser_access_info:
    provider: "{{ zpa_cloud }}"
    name: "Example"

- name: Browser Access Application Segment by ID
  zscaler.zpacloud.zpa_application_segment_browser_access_info:
    provider: "{{ zpa_cloud }}"
    id: "198288282"

"""

RETURN = """
# Returns information on a specified Browser Access Application Segment.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    ba_appsegment_id = module.params.get("id", None)
    ba_appsegment_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    ba_app_segments = []
    if ba_appsegment_id is not None:
        ba_app_segment_box = client.app_segments.get_segment(
            segment_id=ba_appsegment_id
        )
        if ba_app_segment_box is None:
            module.fail_json(
                msg="Failed to retrieve Browser Access Application Segment ID: '%s'"
                % (ba_appsegment_id)
            )
        ba_app_segments = [ba_app_segment_box.to_dict()]
    else:
        ba_app_segments = client.app_segments.list_segments().to_list()
        if ba_appsegment_name is not None:
            ba_app_segment_found = False
            for ba_app_segment in ba_app_segments:
                if ba_app_segment.get("name") == ba_appsegment_name:
                    ba_app_segment_found = True
                    ba_app_segments = [ba_app_segment]
                    break
            if not ba_app_segment_found:
                module.fail_json(
                    msg="Failed to retrieve Browser Access Certificate Name: '%s'"
                    % (ba_appsegment_name)
                )
    module.exit_json(changed=False, data=ba_app_segments)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
