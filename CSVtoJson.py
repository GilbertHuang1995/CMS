import numpy as np
import pandas as pd
import json
import sys
import warnings
import os
warnings.filterwarnings('ignore')


def Genarate_Json(source):
    print('Doing Genarate_Json')
    dict_result = {}
    count = 0
    for Gateway in list(set(source.Gateway.values)):
        if str(Gateway) == 'nan' or Gateway==None or Gateway==np.nan:
            print('Gateway is empty')
            continue
        tmp_source_IP = source[source.Gateway==Gateway]
        dict_result[f'{count}'] = {}
        dict_result[f'{count}']['IP'] = Gateway
        dict_result[f'{count}']['gwID'] = tmp_source_IP['UIG ID'].values[0]
        dict_result[f'{count}']['IT_Broker'] = {}
        dict_result[f'{count}']['IT_Broker']['Host'] = str(tmp_source_IP['Broker'].values[0])+'/'+str(tmp_source_IP['port'].values[0])
        dict_result[f'{count}']['IT_Broker']['Pass'] = str(tmp_source_IP['account'].values[0])+'/'+str(tmp_source_IP['password'].values[0])
        # dict_result[f'{count}']['gwID'] = source[source['IP']==Gateway]['UIG ID'].values[0]
        dict_result[f'{count}']['ports']={}



        for port_ID in tmp_source_IP['Port ID'].values:
            if str(port_ID) == 'nan' or port_ID == None or port_ID == np.nan:
                print('port_ID is empty')
                continue
            tmp_source_Port_ID = tmp_source_IP[tmp_source_IP['Port ID']==port_ID]
            dict_result[f'{count}']['ports'][f'{port_ID}'] = {}
            dict_result[f'{count}']['ports'][f'{port_ID}']['portID'] = port_ID

            dict_result[f'{count}']['ports'][f'{port_ID}']['portName'] = tmp_source_Port_ID['Port Name'].values[0]
            dict_result[f'{count}']['ports'][f'{port_ID}']['portType'] = tmp_source_Port_ID['Port Type'].values[0]
            dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'] = {}

            for slave in tmp_source_Port_ID['Slave ID'].values:
                if str(slave) == 'nan' or slave == None or slave == np.nan:
                    print('slave is empty')
                    continue
                tmp_source_slave = tmp_source_Port_ID[tmp_source_Port_ID['Slave ID'] == slave]

                dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}'] = {}
                dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}']['slaveID'] = slave
                dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}']['toolHost'] = tmp_source_slave['Tool Host'].values[0]
                dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}']['toolProtocol'] = tmp_source_slave['Tool protocol'].values[0]
                dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}']['toolType'] = tmp_source_slave['Tool Type'].values[0]
                dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}']['interval'] = tmp_source_slave['取樣點數'].values[0]
                dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}']['channels'] = {}

                channel_count = 0
                for channel in tmp_source_slave['Channel ID'].values:
                    if str(channel) == 'nan' or channel == None or channel == np.nan:
                        print('channel is empty')
                        continue
                    dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}']['channels'][f'{channel_count}'] = {}
                    dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}']['channels'][f'{channel_count}']['channelID'] = channel_count
                    dict_result[f'{count}']['ports'][f'{port_ID}']['slaves'][f'{slave}']['channels'][f'{channel_count}']['toolCH'] = tmp_source_slave[source['Channel ID']==channel]['Channel ID'].values[0]
                    channel_count = channel_count +1

        count = count+1

    return dict_result

def get_key(key):
    try:
        return int(key)
    except ValueError:
        return key
def append_data(dict_org, dict_new):
    if dict_new['IP']==dict_org['IP'] and dict_new['IT_Broker']==dict_org['IT_Broker']:
        print('Do APPEND')
        for k_ports,v_ports in dict_new['ports'].items():
            if k_ports not in dict_org['ports'].keys():
                # different port
                dict_org['ports'][k_ports]=v_ports
            elif dict_org['ports'][k_ports]['portID']==dict_new['ports'][k_ports]['portID'] and \
                dict_org['ports'][k_ports]['portName']==dict_new['ports'][k_ports]['portName'] and \
                    dict_org['ports'][k_ports]['portType']==dict_new['ports'][k_ports]['portType']:
                # Same port
                for k_slave, v_slave in dict_new['ports'][k_ports]['slaves'].items():
                    print()
                    if k_slave not in dict_org['ports'][k_ports]['slaves'].keys():
                        # different slave
                        dict_org['ports'][k_ports]['slaves'][k_slave] = v_slave
                    elif dict_org['ports'][k_ports]['slaves'][k_slave]['slaveID'] == dict_new['ports'][k_ports]['slaves'][k_slave]['slaveID'] and \
                            dict_org['ports'][k_ports]['slaves'][k_slave]['toolHost'] == dict_new['ports'][k_ports]['slaves'][k_slave]['toolHost'] and \
                            dict_org['ports'][k_ports]['slaves'][k_slave]['toolProtocol'] == dict_new['ports'][k_ports]['slaves'][k_slave]['toolProtocol'] and \
                            dict_org['ports'][k_ports]['slaves'][k_slave]['toolType'] == dict_new['ports'][k_ports]['slaves'][k_slave]['toolType'] and\
                        dict_org['ports'][k_ports]['slaves'][k_slave]['interval'] == dict_new['ports'][k_ports]['slaves'][k_slave]['interval']:

                        # Same slave
                        l_toolCH_org=[]
                        for k_channel_org, v_channel_org in dict_org['ports'][k_ports]['slaves'][k_slave]['channels'].items():
                            l_toolCH_org.append(v_channel_org['toolCH'])

                        for k_channel, v_channel in dict_new['ports'][k_ports]['slaves'][k_slave]['channels'].items():
                            if v_channel['toolCH'] in l_toolCH_org:
                                # Same toolCH
                                print(f'Channel is already in original file at port {k_ports} slave {k_slave} Channel {k_channel} ')
                            else:
                                max_chaneel = max([int(i) for i in list(dict_org['ports'][k_ports]['slaves'][k_slave]['channels'].keys())])+2 if len(dict_org['ports'][k_ports]['slaves'][k_slave]['channels'].keys())!=0 else 1
                                for count_channel in range(max_chaneel):
                                    if count_channel not in [int(i) for i in list(dict_org['ports'][k_ports]['slaves'][k_slave]['channels'].keys())]:
                                        # different toolCH
                                        dict_org['ports'][k_ports]['slaves'][k_slave]['channels'][count_channel] = {'channelID':count_channel , 'toolCH': v_channel['toolCH']}
                                        break
                        dict_org['ports'][k_ports]['slaves'][k_slave]['channels'] = dict(sorted(dict_org['ports'][k_ports]['slaves'][k_slave]['channels'].items(), key=lambda item: int(item[0])))
                    else:
                        print(f"slaveID ,toolHost, toolProtocol, toolType or interval at port {k_ports} slave {k_slave}  ")

                dict_org['ports'][k_ports]['slaves'] = dict(sorted(dict_org['ports'][k_ports]['slaves'].items(),key=lambda item: int(item[0])))

            else:
                print(f"portID ,portName or portType at port {k_ports} ")

        dict_org['ports']= dict(sorted(dict_org['ports'].items(), key=lambda item: int(item[0])))


    else:
        print(f"Org IP={dict_org['IP']}, IT_Broker={dict_org['IT_Broker']}, Pass={dict_org['Pass']}")
        print(f"New IP={dict_new['IP']}, IT_Broker={dict_new['IT_Broker']}, Pass={dict_new['Pass']}")

    return dict_org

if __name__ == '__main__':

    try:
        path_source = sys.argv[1]
        IP_destination = sys.argv[2]
        file_destination = rf'\\{IP_destination}\RPA_Shared\DaYou\CMS_config\config.json'
    except:
        path_source = fr'C:\Users\00074290\Desktop\DaYou\CMS\UIG_v1.xlsx'
        IP_destination = '10.21.90.152'
        file_destination = rf'\\{IP_destination}\RPA_Shared\DaYou\CMS_config\config.json'


    source = pd.read_excel(rf'{path_source}')
    source.rename(columns=source.iloc[1], inplace=True)
    source = source[2:]
    dict_result = Genarate_Json(source)

    for k, v in dict_result.items():
        IP_destination = v['IP']
        file_destination = rf'\\{IP_destination}\RPA_Shared\DaYou\CMS_config\config.json'
        if os.path.exists(file_destination):
            print(f'READING   {file_destination}  \n\n')
            # Do append
            jsonFile = open(file_destination, 'r')
            a = json.load(jsonFile)
            result = append_data(a,v)
            json_object = json.dumps(result, indent=4)
            with open(file_destination, 'w') as outfile:
                outfile.write(json_object)
        else:
            # Create NEW
            print(f'NoNONO   {file_destination}  FILE FOUND\n\n')
            json_object = json.dumps(v, indent=4)
            try:
                with open(file_destination, 'w') as outfile:
                    outfile.write(json_object)
            except Exception as e:
                print(e)
                print(f'Write to {file_destination}  FAIL')



