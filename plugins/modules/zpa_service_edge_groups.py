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
module: zpa_service_edge_groups
short_description: Create an Service Edge Group in the ZPA Cloud.
description:
  - This module creates/update/delete an Service Edge Group in the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
    - zscaler.zpacloud.fragments.credentials_set
    - zscaler.zpacloud.fragments.provider
    - zscaler.zpacloud.fragments.enabled_state
options:
  name:
    description:
      - Name of the Service Edge Group.
    required: true
    type: str
  description:
    description: ""
    required: false
    type: str
  connectors:
    description: "Connectors"
    required: false
    type: list
    elements: dict
    suboptions:
      name:
        description: "Name of the Service Edge Group."
        required: false
        type: str
      id:
        description: "id of the Service Edge Group."
        required: false
        type: str
  id:
    description: "ID of the Service Edge Group."
    required: false
    type: str
  city_country:
    description:
        - City Country of the Service Edge Group.
    type: str
  country_code:
    description:
      - Country code of the Service Edge Group.
    type: str
  dns_query_type:
    description:
      - Whether to enable IPv4 or IPv6, or both, for DNS resolution of all applications in the Service Edge Group.
    type: str
    choices:
        - IPV4_IPV6
        - IPV4
        - IPV6
    default: IPV4_IPV6
  enabled:
    description:
      - Whether this Service Edge Group is enabled or not.
    type: bool
    default: true
  latitude:
    description:
      - Latitude of the Service Edge Group. Integer or decimal. With values in the range of -90 to 90.
    required: false
    type: str
  location:
    description:
      - Location of the Service Edge Group.
    required: false
    type: str
  longitude:
    description:
      - Longitude of the Service Edge Group. Integer or decimal. With values in the range of -180 to 180.
    required: false
    type: str
  lss_app_connector_group:
    description:
      - LSS Service Edge Group
    required: false
    type: str
  upgrade_day:
    description:
      - App Connectors in this group will attempt to update to a newer version of the software during this specified day.
      - List of valid days (i.e., Sunday, Monday).
    default: SUNDAY
    type: str
  upgrade_time_in_secs:
    description:
      - App Connectors in this group will attempt to update to a newer version of the software during this specified time.
      - Integer in seconds (i.e., -66600). The integer should be greater than or equal to 0 and less than 86400, in 15 minute intervals.
    default: '66600'
    type: str
  override_version_profile:
    description:
      - App Connectors in this group will attempt to update to a newer version of the software during this specified time.
      - Integer in seconds (i.e., -66600). The integer should be greater than or equal to 0 and less than 86400, in 15 minute intervals.
    required: false
    type: bool
    default: false
  version_profile_id:
    description:
      - ID of the version profile. To learn more, see Version Profile Use Cases.
      - This value is required, if the value for overrideVersionProfile is set to true.
    required: false
    type: str
    default: '0'
    choices:
      - '0'
      - '1'
      - '2'
  version_profile_name:
    description:
      - Name of the version profile.
    required: false
    type: str
"""

EXAMPLES = """
- name: Create/Update/Delete an Service Edge Group
  zscaler.zpacloud.zpa_service_edge_groups:
    provider: "{{ zpa_cloud }}"
    name: "Example"
    description: "Example2"
    enabled: true
    city_country: "California, US"
    country_code: "US"
    latitude: "37.3382082"
    longitude: "-121.8863286"
    location: "San Jose, CA, USA"
    upgrade_day: "SUNDAY"
    upgrade_time_in_secs: "66600"
    override_version_profile: true
    version_profile_id: "0"
    dns_query_type: "IPV4"
"""

RETURN = """
# The newly created Service Edge Group resource record.
"""


from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    validate_latitude,
    validate_longitude,
    diff_suppress_func_coordinate,
    deleteNone,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)

    latitude = module.params.get("latitude")
    longitude = module.params.get("longitude")

    group = dict()
    params = [
        "id",
        "name",
        "description",
        "enabled",
        "city_country",
        "country_code",
        "latitude",
        "longitude",
        "location",
        "is_public",
        "upgrade_day",
        "upgrade_time_in_secs",
        "dns_query_type",
        "override_version_profile",
        "version_profile_id",
        "version_profile_name",
        "use_in_dr_mode",
        "trusted_networks_ids",
    ]
    for param_name in params:
        group[param_name] = module.params.get(param_name, None)
    group_id = group.get("id", None)
    group_name = group.get("name", None)
    existing_group = None
    if group_id is not None:
        group_box = client.service_edges.get_service_edge_group(group_id=group_id)
        if group_box is not None:
            existing_group = group_box.to_dict()
    elif group_name is not None:
        groups = client.service_edges.list_service_edge_groups().to_list()
        for group_ in groups:
            if group_.get("name") == group_name:
                existing_group = group_
    if existing_group is not None:
        id = existing_group.get("id")
        existing_group.update(group)
        existing_group["id"] = id

    if state == "present":
        if latitude is not None and longitude is not None:
            lat_errors = validate_latitude(latitude)
            lon_errors = validate_longitude(longitude)

            if lat_errors or lon_errors:
                all_errors = lat_errors + lon_errors
                module.fail_json(msg=", ".join(all_errors))

        if existing_group is not None:
            """Update"""
            # Check if latitude and longitude need to be updated
            existing_lat = existing_group.get("latitude")
            new_lat = group.get("latitude")
            if new_lat is not None:  # Check if new_lat is not None before comparing
                if diff_suppress_func_coordinate(existing_lat, new_lat):
                    existing_group[
                        "latitude"
                    ] = existing_lat  # reset to original if they're deemed equal
            else:
                existing_group[
                    "latitude"
                ] = existing_lat  # If new_lat is None, keep the existing value

            existing_long = existing_group.get("longitude")
            new_long = group.get("longitude")
            if new_long is not None:  # Check if new_long is not None before comparing
                if diff_suppress_func_coordinate(existing_long, new_long):
                    existing_group[
                        "longitude"
                    ] = existing_long  # reset to original if they're deemed equal
            else:
                existing_group[
                    "longitude"
                ] = existing_long  # If new_long is None, keep the existing value

            existing_group = deleteNone(
                dict(
                    group_id=existing_group.get("id"),
                    name=existing_group.get("name"),
                    description=existing_group.get("description"),
                    enabled=existing_group.get("enabled"),
                    city_country=existing_group.get("city_country"),
                    country_code=existing_group.get("country_code"),
                    latitude=existing_group.get("latitude"),
                    longitude=existing_group.get("longitude"),
                    is_public=existing_group.get("is_public"),
                    service_edge_ids=existing_group.get("service_edge_ids"),
                    location=existing_group.get("location"),
                    upgrade_day=existing_group.get("upgrade_day"),
                    upgrade_time_in_secs=existing_group.get("upgrade_time_in_secs"),
                    dns_query_type=existing_group.get("dns_query_type"),
                    override_version_profile=existing_group.get(
                        "override_version_profile"
                    ),
                    version_profile_id=existing_group.get("version_profile_id"),
                    version_profile_name=existing_group.get("version_profile_name"),
                    use_in_dr_mode=existing_group.get("use_in_dr_mode"),
                    trusted_networks_ids=existing_group.get("trusted_networks_ids"),
                )
            )
            existing_group = client.service_edges.update_service_edge_group(
                **existing_group
            ).to_dict()
            module.exit_json(changed=True, data=existing_group)
        else:
            """Create"""
            group = deleteNone(
                dict(
                    name=group.get("name"),
                    description=group.get("description"),
                    address=group.get("address"),
                    enable=group.get("enable"),
                    latitude=group.get("latitude"),
                    location=group.get("location"),
                    longitude=group.get("longitude"),
                    city_country=group.get("city_country"),
                    country_code=group.get("country_code"),
                    is_public=group.get("is_public"),
                    service_edge_ids=group.get("service_edge_ids"),
                    upgrade_day=group.get("upgrade_day"),
                    upgrade_time_in_secs=group.get("upgrade_time_in_secs"),
                    dns_query_type=group.get("dns_query_type"),
                    override_version_profile=group.get("override_version_profile"),
                    version_profile_id=group.get("version_profile_id"),
                    version_profile_name=group.get("version_profile_name"),
                    use_in_dr_mode=group.get("use_in_dr_mode"),
                    trusted_networks_ids=group.get("trusted_networks_ids"),
                )
            )
            group = client.service_edges.add_service_edge_group(**group).to_dict()
            module.exit_json(changed=True, data=group)
    elif state == "absent":
        if existing_group is not None and existing_group.get("id") is not None:
            code = client.service_edges.delete_service_edge_group(
                service_edge_group_id=existing_group.get("id")
            )
            if code > 299:
                module.exit_json(changed=False, data=None)
            module.exit_json(changed=True, data=existing_group)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    id_name_spec = dict(
        type="list",
        elements="dict",
        options=dict(
            id=dict(type="str", required=False), name=dict(type="str", required=False)
        ),
        required=False,
    )
    argument_spec.update(
        service_edge_ids=id_name_spec,
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", default=True, required=False),
        city_country=dict(type="str", required=False),
        country_code=dict(type="str", required=False),
        is_public=dict(type="str", required=False),
        dns_query_type=dict(
            type="str",
            choices=["IPV4_IPV6", "IPV4", "IPV6"],
            required=False,
            default="IPV4_IPV6",
        ),
        latitude=dict(type="str", required=False),
        location=dict(type="str", required=False),
        longitude=dict(type="str", required=False),
        upgrade_day=dict(
            type="str",
            choices=[
                "MONDAY",
                "TUESDAY",
                "WEDNESDAY",
                "THURSDAY",
                "FRIDAY",
                "SATURDAY",
                "SUNDAY",
            ],
            default="SUNDAY",
            required=False,
        ),
        upgrade_time_in_secs=dict(type="str", default="66600", required=False),
        override_version_profile=dict(type="bool", default=False, required=False),
        version_profile_id=dict(
            type="str", choices=["0", "1", "2"], default="0", required=False
        ),
        version_profile_name=dict(
            type="str",
            choices=["Default", "Previous Default", "New Release"],
            required=False,
        ),
        use_in_dr_mode=dict(type="bool", default=False, required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
