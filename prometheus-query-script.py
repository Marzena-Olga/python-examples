#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script prepare tickets on Jira from Prometheus metrics.
# Author: Marzena Kupniewska
# Maintainer: Marzena Kupniewska

import urllib3
import requests
import base64
import os
import json
import sys
import argparse
import smtplib
from email.message import EmailMessage


# GDN CMS OPS@LHG  gdn_cms_ops

def send_mail(to_email='email@email.com', subject='Monthly upgrade version ticket generator', message='', server='relay.api',
              from_email='email2@email.com', passwd=''):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    #msg['To'] = ', '.join(to_email)
    msg['To'] = to_email
    msg.set_content(message)
    print(msg)
    server = smtplib.SMTP(server, 587)
    server.starttls()
    server.set_debuglevel(1)
    server.login('login', passwd)
    server.send_message(msg)
    server.quit()
    print('successfully sent the mail.')

def get_jira_data(key=''):  # function to test connection to jira
    print('Get JIRA data')
    # tok = jlogin + ':' + jpassword
    # encoded_tok = base64.b64encode(tok.encode()).decode()
    # headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    url = 'https://jira.com/rest/api/latest/search?jql=project={0}'.format(key)
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    print(r)
    z = (r.json())
    # print(z['issues'])
    # issues_list = z['issues']
    # for i in issues_list:
    #    print(i)
    print(json.dumps(z, indent=4))


def create_jira_ticket(fields_json):  # function create jira ticket
    # tok = jlogin + ':' + jpassword
    # encoded_tok = base64.b64encode(tok.encode()).decode()
    # headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    url = 'https://jira.com/rest/api/2/issue/'
    print('Execute request(json):')
    print(fields_json)
    response = requests.request("POST", url, verify=False, proxies=proxy, data=fields_json,
                                headers=headers)  # , auth=auth)
    print(response.status_code)
    print('Result:', response.json())
    result = response.json()
    if response.status_code == 201:
        ticket = result['key']
        ticket_url = ('https://jira.com/browse/{0}').format(ticket)
        print(ticket_url)
        return ticket_url
    else:
        print("No ticket")
        return ''


def prepare_jira_json(key, table_dict, project):  # function prepare jira json with summary, description and reporter
    final_description = str()
    head = '||Env||Application||Team||Installed||Available||For update||Updated by||\n'
    # print(table_dict)
    # print(table_dict.keys())
    prg_keys = list(table_dict.keys())
    # print(prg_keys)

    for i in prg_keys:
        # print(i)
        app_list = table_dict[i]
        # print(app_list)
        description = head
        for j in app_list:
            # print(i)
            upd = ' '
            if (j[3] != j[4]):
                upd = 'YES'
            d = ('|{0}|{1}|{2}|{3}|{4}|{5}| |\n').format(j[0], j[1], j[2], j[3], j[4], upd)
            description = description + d
        final_description = final_description + description

    print('Tables:')
    print(final_description)

    assignee = 'JIRAUSER01'
    a_name = 'jira_user'
    # print(assignee)
    if project.find('project-string1') != -1:
        assignee = 'jirauser1'  
        a_name = 'jirauser1'
    if project.find('project-string2') != -1:
        assignee = 'jirauser2'  
        a_name = 'jirauser2'
    if project.find('project-string3') != -1:
        assignee = 'jirauser3'  
        a_name = 'jirauser3'
    if project.find('project-string4') != -1:
        assignee = 'jirauser4'  
        a_name = 'jirauser4'
    print('Assignee:', assignee, ' ', a_name)

    jira_json = json.dumps({  # for single ticket
        "fields":
            {
                "project":
                    {
                        "key": key
                    },
                "assignee":
                    {
                        "key": "jirauser",
                        "name": "John",
                        "displayName": "John Smith",
                        "emailAddress": "email1@email.com"
                    },
                "priority": {"id": "10000"},
                "summary": ('{0} Application version check').format(project),
                "description": final_description,
                "timetracking": {},
                "issuetype":
                    {
                        "name": "Task"
                    }
            }
    })

    jira_json = json.dumps({  # for subtask
        "fields":
            {
                "parent": {
                    "id": "is_parrent_ticket",
                    "key": "key_parent_ticket",
                    "self": "https://jira.com/rest/api/2/issue/3393894",
                    "fields": {
                        "summary": "monthly application version check",
                        "priority": {"id": "10"},
                        "issuetype": {"name": "Task"}
                    },
                },
                "project":
                    {
                        "key": key
                    },
                "assignee":
                    {
                        "key": assignee, 
                        "name": a_name 
                    },
                "priority": {"id": "10"},
                "summary": ('{0} Application version check').format(project),
                "description": final_description,
                "timetracking": {},
                "issuetype": {"name": "Sub-task"}
            }
    })

    print('Jira json:')
    # print(jira_json)
    # print(type(jira_json))
    jd = json.loads(jira_json)
    # print(type(d))
    print(json.dumps(jd, indent=4))
    return jira_json


def get_prom_data2(metric, prometheus_url):  # function get metrich from Prometheus (as json) by REST-API
    tok = plogin + ':' + ppassword
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    r = str()
    z = json.dumps({'data': {'result': []}})
    z = json.loads(z)
    # url = 'https://prometheus.local/api/v1/query?query=node_app_available_version_info'
    url = ('{0}api/v1/query?query={1}').format(prometheus_url, metric)
    print(url)
    try:
        r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    except:
        print('No response')
    # print(r.status_code)
    print(r)
    # print(type(r))
    # print(r.content)
    try:
        z = (r.json())
    except:
        print('No json return')
    print(z)
    # print(json.dumps(z, indent=4))
    return z


def compare_versions(ava_ver,
                     current_ver):  # function join tables installed versions and available versions of applications
    # print(ava_ver)
    # print(current_ver)
    return_list = list()
    # print(json.dumps(ava_ver, indent=4))
    ava_ver_list = (ava_ver['data']['result'])
    # print('*****************************************************************************************************')
    for i in ava_ver_list:
        # print(i)
        j = i['metric']
        # print(j['application'], j['available_version_id'], j['environment'], j['hostname'])

    print(
        '***********************************************************************************************************************')
    current_ver_list = (current_ver['data']['result'])
    for i in current_ver_list:
        # print(i)
        j = i['metric']
        # print(j)
        for k in ava_ver_list:
            if j['application'] == k['metric']['application']:
                ver = k['metric']['available_version_id']
        print("| %10s | %20s | %10s | %20s | %20s | %20s | " % (
            j['environment'], j['application'], j['app_instance'], j['installed_version_id'], j['hostname'], ver))
        small_list = [j['environment'], j['application'], j['app_instance'], j['installed_version_id'], ver]
        return_list.append(small_list)
    print(
        '***********************************************************************************************************************')
    return return_list


def prepare_table(
        update_list):  # function prepare table as unique (as dictionary of lists) with information which application needs upgrade
    return_dict = dict()
    id_list = set()

    for i in update_list:
        id_list.add(i[0])
    print('ID_List:', id_list)

    for j in id_list:
        tmp_list = list()
        program_set = set()
        for i in update_list:
            if (i[0] == j and i[2] == 'GDN'):
                tmp_list.append(i)
                program_set.add(i[1])
        print('Applications: ', program_set)
        # print(tmp_list)
        temp_list = list()
        for k in program_set:
            tl = list()
            for l in tmp_list:
                if k == l[1]:
                    tl = l
            temp_list.append(tl)
        return_dict[j] = temp_list
    print('************************************')
    print(return_dict)
    print('************************************')

    return return_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Script required path eq:  --token=jira_token --url=https://prometheus.local/ --login=admin --project=Project --password=admin --smtp_pass=(PASS)"
    )
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--url", required=True, type=str)
    parser.add_argument("--login", required=True, type=str)
    parser.add_argument("--project", required=True, type=str)
    parser.add_argument("--password", required=True, type=str)
    parser.add_argument("--smtp_pass", required=True, type=str)
    args = parser.parse_args()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    #params:
    encoded_tok = args.token
    prometheus_url = args.url
    plogin = args.login
    project = args.project
    ppassword = args.password
    smtp_pass = args.smtp_pass

    # jira project key:
    key = 'GDNCMSOPS'

    # 'BUILD_DEFINITIONNAME': 'Prom_TO_Jira_PROD',

    build = os.getenv('BUILD_DEFINITIONNAME')
    print('BUILD_DEFINITIONNAME:', build)

    email = 'email@email.com'
    if project.find('string-proj1') != -1:
        email = 'email1@email.com'
    if project.find('string-proj2') != -1:
        email = 'email2@email.com'
    if project.find('string-proj3') != -1:
        email = 'email3@email.com'
    if project.find('string-proj4') != -1:
        email = 'email4@email.com'
    print('E-Mail:', email)

    ava_ver = get_prom_data2('node_app_available_version_info', prometheus_url)
    current_ver = get_prom_data2('node_app_installed_version_info', prometheus_url)

    # print(len(ava_ver['data']['result']))
    # print(len(current_ver['data']['result']))
    m1 = (len(current_ver['data']['result']))
    m2 = (len(ava_ver['data']['result']))
    if (m1 == 0) or (m2 == 0):
        info = ("Error: One or more metrics do not works on {0} !!!").format(prometheus_url)
        print('*********************************************************************************')
        print(info)
        print('*********************************************************************************')
        message = ('The ticket was not created correctly - metric from Prometheus are invalid - project {0}').format(project)
        print(message,' ',email )
        send_mail(to_email='email@email.com', subject='Monthly upgrade version ticket generator', message=message, server='relay.api', from_email=email, passwd=smtp_pass )
        r = -1
    else:
        update_list = compare_versions(ava_ver, current_ver)
        table_dict = prepare_table(update_list)
        jf = prepare_jira_json(key, table_dict, project)
        ticket_addr = create_jira_ticket(jf)
        # final_ticket_list.append(ticket_addr)
        message = ('The ticket was created correctly for project {0}: {1}').format(project, ticket_addr)
        print(message,' ',email )
        send_mail(to_email='email@email.com', subject='Monthly upgrade version ticket generator', message=message, server='relay.api', from_email=email, passwd=smtp_pass)
        print('*********************************************************************************')
        print("Ticket:", ticket_addr)
        r = 0

    sys.exit(r)

    # get_jira_data(key)
