### v1.1.1

import requests
import xmltodict
import pandas as pd
import datetime
import numpy as np
from re import sub
from pathlib import Path


class ArgusPossibilityCurves:

    def __init__(self, username, password):
        self.category_ids = None
        self.OBOS_list = None
        self.argus_username = username
        self.argus_password = password
        self.auth_token = None
        self.df_meta = None
        self.version = "1.1.1"

    def authenticate(self):

        print("Getting authentication token...")
        try:
            self.auth_token = self.getToken()
        except:
            print("ERROR: Could not authenticate! Check credentials.")
        else:
            print("    Authentication successful")

    def getToken(self):

        """ Main function to return Argus prices Via Soap """
        url = "https://www.argusmedia.com/ArgusWSVSTO/ArgusOnline.asmx?wsdl"
        headers = {'content-type': 'text/xml', 'SOAPAction': "http://tempuri.org/Authenticate"}
        # ------------------------------Authenticate
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
            <soapenv:Header/>
            <soapenv:Body>
                <tem:Authenticate>
                    <!--Optional:-->
                    <tem:username>%s</tem:username>
                    <!--Optional:-->
                    <tem:password>%s</tem:password>
                </tem:Authenticate>
            </soapenv:Body>
        </soapenv:Envelope>"""
        # print(body)
        response = requests.post(url, data=body % (self.argus_username, self.argus_password), headers=headers)
        # print (response.content)
        xml_string = response.text
        xml_dict = xmltodict.parse(xml_string)
        auth_token = xml_dict['soap:Envelope']['soap:Body']['AuthenticateResponse']['AuthenticateResult']['AuthToken']
        
        return auth_token

    def getMetadataCSV(self, filepath=None, force_update_from_remote=True):
        if Path(filepath).is_file() and not force_update_from_remote:

            try:
                self.df_meta = pd.read_csv(filepath, dtype=str)
            except:
                print("ERROR: Could not open metadata file")
        else:
            print("Loading metadata from remote...")
            if not self.auth_token is None:
                self.df_meta = self.getPricesMetadata(code_list=[], cat_list=[])
                if not filepath is None:
                    try:
                        self.df_meta.to_csv(filepath, index=False)
                    except:
                        print("ERROR: could not write to " + filepath)
                    else:
                        print(filepath + " saved to folder")
            else:
                print("ERROR: Authenticate first")

    def getPricesMetadata(self, code_list=[], cat_list=[], quote_active_yn='Y'):

        print("Retrieving metadata from remote server...")

        url = "https://www.argusmedia.com/ArgusWSVSTO/ArgusOnline.asmx?wsdl"

        # ------------------------------ Define GetTables request

        headers = {'content-type': 'text/xml', 'SOAPAction': "http://tempuri.org/GetTables"}

        getTablesBody = """<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:tem='http://tempuri.org/'>
            <soapenv:Header/>
            <soapenv:Body>
                <tem:GetTables>
                <tem:authToken>%s</tem:authToken>
                <tem:tableNames>
                <tem:string>%s</tem:string>
                </tem:tableNames>
                </tem:GetTables>
            </soapenv:Body>
        </soapenv:Envelope>"""

        # ------------------------------ GET PRICE CATEGORY MAPPING
        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_PRICE_CATEGORY'), headers=headers)
        #xml_dict = xmltodict.parse(response.text)
        df_price_category = pd.DataFrame(data=xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_PRICE_CATEGORY'))
        df_price_category = df_price_category[['ID', 'DESCRIPTION']].rename(columns={"ID": "CATEGORY_ID", "DESCRIPTION": "CATEGORY"})

        # ------------------------------ GET CODE CATEGORY MAPPING
        #print("Getting code_category")
        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_CODE_CATEGORY'), headers=headers)
        #xml_dict = xmltodict.parse(response.text)
        df_code_category = pd.DataFrame(data=xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_CODE_CATEGORY'))[["CODE_ID", "CATEGORY_ID"]]
        df_code_category['CATEGORY_ID'].astype(str)
        #xml_code_dict = xml_dict['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram'][
        #   'NewDataSet'].get('V_CODE_CATEGORY').[['CODE_ID', 'CATEGORY_ID']]

        code_list.extend(df_code_category[df_code_category['CATEGORY_ID'].isin(cat_list)]['CODE_ID'])
        code_list = list(dict.fromkeys(code_list))


        # ------------------------------ GET TIMESTAMPS
        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_TIMESTAMP'), headers=headers)
        df_timestamp = pd.DataFrame(data=xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_TIMESTAMP'))
        df_timestamp = df_timestamp[['TIME_STAMP_ID', 'DESCRIPTION']].rename(columns={"TIME_STAMP_ID": "TIMESTAMP_ID", "DESCRIPTION": "TIMESTAMP"})

        # ------------------------------ GET PRICETYPE
        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_PRICE_TYPE'), headers=headers)
        df_pricetype = pd.DataFrame(data=xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_PRICE_TYPE'))
        df_pricetype = df_pricetype[['PRICE_TYPE_ID', 'DESCRIPTION']].rename(columns={"DESCRIPTION": "PRICETYPE"})

        # ------------------------------ GET TIMING
        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_TIMING'), headers=headers)
        df_timing = pd.DataFrame(data=xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_TIMING'))
        df_timing = df_timing[['TIMING_ID', 'DESCRIPTION']].rename(columns={"DESCRIPTION": "TIMING"})
        
        # ------------------------------ GET UPLOAD_FREQ
        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_UPLOAD_FREQ'), headers=headers)
        df_upload_freq = pd.DataFrame(data=xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_UPLOAD_FREQ'))
        df_upload_freq = df_upload_freq[['UPLOAD_FREQ_ID', 'DESCRIPTION']].rename(columns={"DESCRIPTION": "UPLOAD_FREQ"})

        # ------------------------------ GET UNITS
        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_UNIT'), headers=headers)
        df_units = pd.DataFrame(data=xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_UNIT'))
        df_units1 = df_units[['UNIT_ID', 'DESCRIPTION']].rename(columns={"UNIT_ID": "UNIT_ID1", "DESCRIPTION": "PRICE_UNIT"})
        df_units2 = df_units[['UNIT_ID', 'DESCRIPTION']].rename(columns={"UNIT_ID": "UNIT_ID2", "DESCRIPTION": "VOL_UNIT"})

        # ------------------------------ GET CODE DETAILS
        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_CODE'), headers=headers)
        df_codes = pd.DataFrame(data=xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_CODE'))
        df_codes = df_codes.drop(['REP_TIMESTAMP', '@diffgr:id', '@msdata:rowOrder'],axis=1).rename(columns={"ACTIVE_YN": "CODE_ACTIVE_YN"})

        #filter codes?
        if len(code_list) > 0:        
            df_codes = df_codes[df_codes['CODE_ID'].isin(code_list)]

        # add categories
        df_codes = pd.merge(df_codes, df_code_category, left_on='CODE_ID', right_on='CODE_ID', how='left')
        df_codes = pd.merge(df_codes, df_price_category, left_on='CATEGORY_ID', right_on='CATEGORY_ID', how='left')
        #df_codes['CATEGORY_ID']

        # add units
        df_codes = pd.merge(df_codes, df_units1, left_on='UNIT_ID1', right_on='UNIT_ID1', how='left')
        df_codes = pd.merge(df_codes, df_units2, left_on='UNIT_ID2', right_on='UNIT_ID2', how='left')
        df_codes['PRICE_UNIT'] = df_codes['PRICE_UNIT'].str.cat(df_codes['VOL_UNIT'], sep="/")

        # ------------------------------ GET QUOTE LIST
        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_QUOTE'), headers=headers)
        xml_dict = xmltodict.parse(response.text)

        quote_dict = xml_dict['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_QUOTE')
        df_quotes = pd.DataFrame(data=quote_dict)
        # df_quotes.set_index('QUOTE_ID', inplace=True)
        df_quotes = df_quotes[df_quotes['CODE_ID'].isin(df_codes['CODE_ID'])].drop(['REP_TIMESTAMP','@diffgr:id','@msdata:rowOrder'], axis=1)

        #filter to exclude only active quotes?
        if quote_active_yn == 'Y':
            df_quotes = df_quotes[df_quotes['ACTIVE_YN'] == 'Y']
        df_quotes = df_quotes.rename(columns={"ACTIVE_YN": "QUOTE_ACTIVE_YN"})
        #df_quotes = df_quotes[df_quotes['CONTINUOUS_FORWARD'].isin(argus_continuous_forward)]

        # Merge all
        df_meta = pd.merge(left=df_codes, right=df_quotes, left_on='CODE_ID', right_on='CODE_ID')
        df_meta = pd.merge(left=df_meta, right=df_timestamp, left_on='TIME_STAMP_ID', right_on='TIMESTAMP_ID')
        df_meta = pd.merge(left=df_meta, right=df_timing, left_on='TIMING_ID', right_on='TIMING_ID')
        df_meta = pd.merge(left=df_meta, right=df_upload_freq, left_on='UPLOAD_FREQ_ID', right_on='UPLOAD_FREQ_ID')
        
        #df_meta = pd.merge(left=df_meta, right=df_pricetype, left_on='PRICE', right_on='TIMING_ID')

        return df_meta


    def getCustomPriceReport(self, df_meta, start_date, end_date, periodicity = "Daily"):

        url = "https://www.argusmedia.com/ArgusWSVSTO/ArgusOnline.asmx?wsdl"

        #------------------------------- get pricetypes
        headers = {'content-type': 'text/xml', 'SOAPAction': "http://tempuri.org/GetTables"}
        getTablesBody = """<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:tem='http://tempuri.org/'>
            <soapenv:Header/>
            <soapenv:Body>
                <tem:GetTables>
                <tem:authToken>%s</tem:authToken>
                <tem:tableNames>
                <tem:string>%s</tem:string>
                </tem:tableNames>
                </tem:GetTables>
            </soapenv:Body>
        </soapenv:Envelope>"""

        response = requests.post(url, data=getTablesBody % (self.auth_token, 'V_PRICE_TYPE'), headers=headers)
        df_pricetype = pd.DataFrame(data=xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetTablesResponse']['GetTablesResult']['diffgr:diffgram']['NewDataSet'].get('V_PRICE_TYPE'))
        df_pricetype = df_pricetype[['PRICE_TYPE_ID', 'DESCRIPTION']].rename(columns={"DESCRIPTION": "PRICETYPE"})    

        # ------------------------------ submit request
        headers = {'content-type': 'text/xml', 'SOAPAction': "http://tempuri.org/GetCustomReport"}
        # headers = {'content-type': 'text/xml', 'SOAPAction': "http://tempuri.org/Authenticate"}

        repoFull = ""

        repoTop = """<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:tem='http://tempuri.org/'>
            <soapenv:Header/>
            <soapenv:Body>
                <tem:GetCustomReport>
                    <tem:authToken>%s</tem:authToken>
                        <tem:pars>
                            <tem:Periodicity>%s</tem:Periodicity>
                            <tem:StartDate>%s</tem:StartDate>
                            <tem:EndDate>%s</tem:EndDate>
                            <tem:ItemList>"""

        repoTop = repoTop % (self.auth_token, periodicity, start_date, end_date)
        
        print(df_meta.head(5))
        for index, row in df_meta.iterrows():
            repoItem = """
            <tem:PriceReportItem>
            <tem:QuoteId>%s</tem:QuoteId>
            <tem:PriceTypeId>-1</tem:PriceTypeId>
            <tem:PriceReportItemID>%s</tem:PriceReportItemID>
            <tem:ForwardPeriod>-1</tem:ForwardPeriod>
            <tem:ForwardYear>-1</tem:ForwardYear>
            <tem:CurrencyUnit>-1</tem:CurrencyUnit>
            <tem:MeasureUnit>-1</tem:MeasureUnit>
            <tem:TimestampId>-1</tem:TimestampId>
            </tem:PriceReportItem>"""
            repoFull = repoFull + (repoItem % (row['QUOTE_ID'], index))

        repoBottom = """</tem:ItemList>
                        </tem:pars>
                        </tem:GetCustomReport>
                        </soapenv:Body>
                        </soapenv:Envelope>"""

        repoBody = repoTop + repoFull + repoBottom

        # submit price request
        response = requests.post(url, data=repoBody, headers=headers)
        repo_dict = xmltodict.parse(response.text)

        repo_dict = repo_dict['soap:Envelope']['soap:Body']['GetCustomReportResponse']['GetCustomReportResult']['diffgr:diffgram']['DSPrice'].get('V_REPO')

        df_repo = pd.DataFrame(data=repo_dict)

        repo_dict = None

        # merge prices and metadata
        df_repo = pd.merge(left=df_repo, right=df_meta[['QUOTE_ID', 'DESCRIPTION', 'SPECIFICATION', 'TIMING_ID', 'TIMESTAMP','TIMING', 'PRICE_UNIT', 'CATEGORY']], left_on='QUOTE_ID',right_on='QUOTE_ID')
        df_repo = df_repo[['REPOSITORY_ID', 'CORRECTION_ID', 'CODE_ID', 'QUOTE_ID', 'PUBLICATION_DATE','DESCRIPTION', 'CATEGORY', 'SPECIFICATION', 'TIMESTAMP', 'CONTINUOUS_FORWARD', 'TIMING_ID', 'PRICETYPE_ID', 'TIMING', 'FORWARD_YEAR', 'FORWARD_PERIOD', 'VALUE', 'PRICE_UNIT']].rename(columns={"SPECIFICATION": "QUANTILE"})
        df_repo = pd.merge(left=df_repo, right=df_pricetype, left_on='PRICETYPE_ID', right_on='PRICE_TYPE_ID')
        # df_repo.groupby(['TIMING_ID','FORWARD_PERIOD','FORWARD_YEAR']).size().reset_index().rename(columns={0:'count'})

        # df_repo = df_repo.head(n=100)
        # datetime.datetime(year=2012, month=2, day=9)

        df_repo['FORWARD_YEAR'] = df_repo['FORWARD_YEAR'].astype(str).astype(int)
        df_repo['FORWARD_PERIOD'] = df_repo['FORWARD_PERIOD'].astype(str).astype(int)
        df_repo['PUBLICATION_DATE'] = df_repo['PUBLICATION_DATE'].astype(str).str[:10]
        df_repo['PUBLICATION_DATE'] = pd.to_datetime(df_repo['PUBLICATION_DATE'], format='%Y-%m-%d')
        df_repo['CODE_ID'] = df_repo['CODE_ID'].astype(str).astype('int64')
        df_repo['QUOTE_ID'] = df_repo['QUOTE_ID'].astype(str).astype('int64')    
        df_repo['DESCRIPTION'] = df_repo['DESCRIPTION'].astype(str)
        df_repo['QUANTILE'] = df_repo['QUANTILE'].astype(str)
        #df_repo['TIMESTAMP_ID'] = df_repo['TIMESTAMP_ID'].astype(int)
        df_repo['CONTINUOUS_FORWARD'] = df_repo['CONTINUOUS_FORWARD'].astype(int)
        df_repo['PRICETYPE_ID'] = df_repo['PRICETYPE_ID'].astype(int)
        df_repo['TIMING_ID'] = df_repo['TIMING_ID'].astype(int)
        df_repo['REPOSITORY_ID'] = df_repo['REPOSITORY_ID'].astype(int)
        df_repo['CORRECTION_ID'] = df_repo['CORRECTION_ID'].astype(int)
        df_repo['VALUE'] = df_repo['VALUE'].astype('float32')
        df_repo['PRICE_UNIT'] = df_repo['PRICE_UNIT'].astype(str)


        # Calculate periods
        #     for codes with day/interval timing
        if len(df_repo[df_repo.TIMING_ID.isin([6,36])]) > 0:                        
            df_repo.loc[df_repo.TIMING_ID.isin([6,36]),'PERIOD'] = pd.to_datetime((df_repo['FORWARD_YEAR'] * 1000 + df_repo['FORWARD_PERIOD']).apply(str),format='%Y%j')             
        
        #     for codes with monthly timing
        if len(df_repo[df_repo['TIMING_ID'] == 11]) > 0:            
            df_repo.loc[df_repo.TIMING_ID == 11, 'PERIOD'] = pd.to_datetime(( \
                                                        (df_repo.loc[
                                                        df_repo.TIMING_ID == 11].FORWARD_YEAR * 10000 + \
                                                        df_repo.loc[
                                                        df_repo.TIMING_ID == 11].FORWARD_PERIOD * 100) + 1).apply(
                                                        str), format='%Y%m%d')            

        output = df_repo.sort_values(by=['DESCRIPTION', 'PUBLICATION_DATE', 'QUOTE_ID'])
        return output



    def get_available_poss_curves(self):
        if self.df_meta is None:
            print("ERROR: Call getMetadataCSV() first to load metadata")
            return None
        else:
            # finds all possibility curves entries in metadata
            unique_cat_ids = set(\
                                 self.df_meta[(self.df_meta['DESCRIPTION'].str.contains('overbought') == False) \
                                              & (self.df_meta['DESCRIPTION'].str.contains('oversold') == False)  \
                                                  & (pd.to_numeric(self.df_meta['CODE_ID'])>6000000)]['CATEGORY_ID'].values)
                        
            category_ids = dict()
            for cat_id in unique_cat_ids:
                description = sub(' possibility curves Q0.[0-9][0-9][0-9][0-9]', '', \
                                  self.df_meta[(self.df_meta['CATEGORY_ID'] == cat_id)].iloc[0]["DESCRIPTION"])
                description = sub(' month$| day$', '', description) + ', ' + \
                    self.df_meta[(self.df_meta['CATEGORY_ID'] == cat_id)].iloc[0]["UPLOAD_FREQ"]
                cat_id = self.df_meta[(self.df_meta['CATEGORY_ID'] == cat_id)].iloc[0]["CATEGORY_ID"]
                category_ids.update({description: cat_id})

            self.category_ids = category_ids
            
        cat_list = list(self.category_ids.keys())                   
        return cat_list

    
    def get_available_obos(self):
        if self.df_meta is None:
            print("ERROR: Call getMetadataCSV() first to load metadata")
            return None
        else:

            self.OBOS_list = list(set(self.df_meta[
                (self.df_meta['DESCRIPTION'].str.contains('overbought')) |
                (self.df_meta['DESCRIPTION'].str.contains('oversold'))                         
                ]['DESCRIPTION'].str.split(pat="possibility",n=1).str[0].str.strip()))
            

        return self.OBOS_list



    def get_data(self, start_date, end_date, categories=[], obos=[], delta_days=365):
        if self.df_meta is None:
            print("ERROR: Call getMetadataCSV() first to load metadata")
            return None
        else:
            if self.category_ids is None:
                self.get_available_poss_curves()
            if self.OBOS_list is None:
                self.get_available_obos()

            category_ids = [self.category_ids[category] for category in categories]
            df_meta = self.df_meta[
                            (self.df_meta['CATEGORY_ID'].isin(category_ids)) | 
                            (self.df_meta['DESCRIPTION'].str.contains('|'.join(obos)) & \
                             self.df_meta['CATEGORY'].str.contains('Overbought') )
                            ]    

            if not len(df_meta)>0:
                print("ERROR: Could not find matches for categories or obos required")
                return None
            else:


                df_output = pd.DataFrame()
                delta = datetime.timedelta(days=delta_days)  #size of window for batching requests


                df_output =  pd.DataFrame()
                while start_date <= end_date:

                    #print(start_date)
                    response = pd.DataFrame()
                    if start_date + delta - datetime.timedelta(days=1) > end_date:        
                        print("Requesting data for " + str(start_date) + " to " + str(end_date) + "...")        
                        try:
                            response = self.getCustomPriceReport(df_meta=df_meta, start_date= str(start_date), end_date= str(end_date))
                            print("    successful")
                        except Exception as e:
                            print(e)
                            print ("ERROR: Could not retrieve data for " + str(start_date) + " to " +  str(end_date))
                    else:
                        print("Requesting data for " + str(start_date)+ " to " +\
                              str(start_date + delta - datetime.timedelta(days=1)) + "...")
                        try:
                            response = self.getCustomPriceReport(df_meta, \
                                                                 str(start_date),\
                                                                     str(start_date + delta - datetime.timedelta(days=1)))
                            print("    successful")
                        except:
                            print("ERROR: Could not retrieve data for " + str(start_date) + " to " + str(end_date))

                    if len(response.index) != 0:
                        if len(df_output.index) == 0:            
                            df_output = response
                            #print(len(df_output.index))
                        else:
                            #df_output = df_output.append(response, ignore_index=True)
                            df_output = pd.concat([df_output,response], ignore_index=True)

                    start_date += delta

        return df_output


    def getPossibilityCurves(self, start_date, end_date, categories):

        print(self.version + " Grabbing PossibilityCurves data...")
        available_poss_curves = self.get_available_poss_curves()
        unavailable = [category for category in categories if not category in available_poss_curves]
        if len(unavailable)>0:
            raise Exception("Some of the categories requested are not available. Check available categories with ArgusPossibilityCurves.get_available_poss_curves()")

        full_data = self.get_data(start_date=start_date, end_date=end_date, categories=categories, obos=[])
        if not full_data is None:
            poss_curves = full_data
            #pivot poss_curves data by QUANTILE
            if not poss_curves.empty:
                poss_curves = poss_curves[poss_curves['QUANTILE'] != 'nan']
                poss_curves = (poss_curves.set_index(["PUBLICATION_DATE", "PERIOD", "CATEGORY", "CONTINUOUS_FORWARD", "TIMESTAMP", "PRICE_UNIT"])
                               .pivot(columns="QUANTILE")['VALUE']
                               .reset_index()
                               .rename_axis(None, axis=1)
                               )
                return poss_curves
            else:
                print("ERROR: Empty dataframe")
                return None
        else:
            return None


    def getOBOS(self, start_date, end_date, obos):

        print(self.version + " Grabbing OBOS data...")
        available_obos = self.get_available_obos()
        unavailable = [obos_level for obos_level in obos if not obos_level in available_obos]
        if len(unavailable)>0:
            raise Exception("Some of the OBOS requested are not available. Check available categories with ArgusPossibilityCurves.get_available_obos()")

        full_data = self.get_data(start_date=start_date, end_date=end_date, categories=[], obos=obos)
        if not full_data is None:
            obos = full_data
            #pivot obos data by series description
            if not obos.empty:
                obos = (obos.set_index(["PERIOD","CONTINUOUS_FORWARD", "TIMESTAMP","PRICE_UNIT"])
                        .pivot(columns="DESCRIPTION")['VALUE']
                        .reset_index()
                        .rename_axis(None, axis=1)
                        )
                return obos
            else:
                print("ERROR: Empty dataframe")
                return None
        else:
            return None


    def calculate_statistics(self, data=None):

        """
            Calculates some statistics based on the cumulative distribution function.
            The calculated statistics are:
                IQR - Inter-quartile range
                Central Skewness
                Tail Skewness
                Downside Tail Risk
                Upside Tail Risk

            Parameters:
                data (Pandas DataFrame): A data frame with the structure of the output of ArgusPossibilityCurves.getPossibilityCurves()

        """

        READY = True
        
        if data is None:
            READY = False
            print("ERROR: Please provide a dataframe with the APC data")
        if len(set(data["CATEGORY"]))>1:
            READY = False
            print("ERROR: Please send data for a single category")

        if READY:
            data = data.copy()
            if not data.index.name == 'PUBLICATION_DATE':
                print("-> Setting pulication data as index")
                data = data.set_index("PUBLICATION_DATE")

            print("Calculating:")
            ### Stat 1: IQR (inter-quartile range)
            print("   IQR - Inter-Quartile Range")
            data["IQR"] = data["0.75"]-data["0.25"]
            
            ### Stat 2 : Central skewness
            print("   Central Skewness")
            data["Central Skewness"] = (data["0.25"]+data["0.75"]-2*data["0.5"]) / (data["0.75"] - data["0.25"])
            
            ### Stat 3: Tail skewness
            print("   Tail Skewness")
            data["Tail Skewness"] = (data["0.0025"]+data["0.9975"]-2*data["0.5"]) / (data["0.9975"] - data["0.0025"])
            
            ### Stat 4: Downside tail risk
            print("   Downside Tail Risk")
            data["Downside Tail Risk"] = data["0.5"]-data["0.0025"]
            
            ### Stat 5: Upside tail risk
            print("   Upside Tail Risk")
            data["Upside Tail Risk"] = data["0.9975"]-data["0.5"]            
        
        return data


    def calculate_trading_signals(self, data=None, IQR_window=None, Skew_window=None):

        """
            Calculates trading signals ("Buy" or "Sell") based on two different strategies.
            Strategy IQR:
                If IQR > IQR_moving_average  -> Sell
                If IQR < IQR_moving_average  -> Buy
            Strategy IQR-Skewness:
                If IQR > IQR_moving_average  AND Central_Skewness < Central_Skewness_moving_average  -> Sell
                If IQR < IQR_moving_average  AND Central_Skewness > Central_Skewness_moving_average  -> Buy        

            Parameters:
                data (Pandas DataFrame): A data frame with the structure of the output of ArgusPossibilityCurves.getPossibilityCurves()
                IQR_window (int): Moving window to calculate rolling IQR mean. Default is 10
                Skew_window (int): Moving window to calculate rolling Central Skewness mean. Default is 10

        """

        READY = True
        out = None
        if data is None:
            READY = False
            print("ERROR: Please provide a dataframe with the APC data")
        if len(set(data["CATEGORY"]))>1:
            READY = False
            print("ERROR: Please send data for a single category")
        
        if READY:
            data = data.copy()
            if IQR_window is None:
                IQR_window = 10
                print("Calculating trading signals using IQR moving window =", IQR_window)
            if Skew_window is None:
                Skew_window = 10
                print("Calculating trading signals using Central Skewness moving window =", Skew_window)

            if not "IQR" in list(data.columns):
                data = self.calculate_statistics(data=data)

            ### Moving average of IQR
            data['IQR Moving Average'] = data.loc[:, 'IQR'].rolling(window=IQR_window).mean()
            ### Moving average of Central Skewness
            data['Central Skewness Moving Average'] = data.loc[:, 'Central Skewness'].rolling(window=Skew_window).mean()

            ### IQR
            data['Signal IQR'] = "neutral"
            data.loc[data['IQR']>data['IQR Moving Average'], 'Signal IQR']  = "Sell"
            data.loc[data['IQR']<data['IQR Moving Average'], 'Signal IQR']  = "Buy"

            ### IQR-Skewness
            data['Signal IQR-Skewness'] = "neutral"
            data.loc[(data['IQR']>data['IQR Moving Average']) & (data['Central Skewness']<data['Central Skewness Moving Average']), 'Signal IQR-Skewness']  = "Sell"
            data.loc[(data['IQR']<data['IQR Moving Average']) & (data['Central Skewness']>data['Central Skewness Moving Average']), 'Signal IQR-Skewness']  = "Buy"

            out = data
            
        return out
    
    def calculate_expected_shortfall(self, data=None, entry_prices=None, label=None):

        """
            Calculates the expected shortfall (for both long and short positions) at user-defined entry points.

            Parameters:
                data (Pandas DataFrame): A data frame with the structure of the output of ArgusPossibilityCurves.getPossibilityCurves()
                entry_prices (float of list of floats): The levels (entry points) from which to calculate the expected shortfall. If a single value is given,
                                    this will be used for all entries in "data". Otherwise, it expects a list of the same length as "data"
                label (str, optional): Adds a label to the added shortfall columns in the returned dataframe

        """

        READY = True
        out = None
        if data is None:
            READY = False
            print("ERROR: Please provide a dataframe with the APC data")
        if len(set(data["CATEGORY"]))>1:
            READY = False
            print("ERROR: Please send data for a single category")
        if entry_prices is None:
            READY = False
            print("ERROR: Please provide the levels to calculate the expected shortfall")
        else:
            if not (type(entry_prices) == int or type(entry_prices) == float):
                if not type(entry_prices) == list:
                    print("ERROR: Please provide the shortfall levels as a single value or a list of values of the same length as the data")
                    READY = False
                elif not len(entry_prices)==len(data):
                    print("ERROR: Please provide the shortfall levels as a single value or a list of values of the same length as the data")
                    READY = False

        if READY:
            data = data.copy()
            if not data.index.name == 'PUBLICATION_DATE':
                print("-> Setting pulication data as index")
                data = data.set_index("PUBLICATION_DATE")

            if not type(entry_prices) == list:
                entry_prices = [entry_prices]*len(data)

            # Grabs available quantiles
            locs = [col.replace('.', '', 1).isdigit()
                    for col in list(data.columns)]
            quantiles = list()
            for i in range(0, len(locs)):
                if locs[i] is True:
                    quantiles = pd.concat(
                        [pd.Series(quantiles), pd.Series(list(data.columns)[i])])

            # Runs the different dates
            colname1 = "Expected Shortfall (LONG)"
            colname2 = "Expected Shortfall (SHORT)"
            if not label is None:
                colname1 = colname1 + " - " + label
                colname2 = colname2 + " - " + label
            data[colname1] = None
            data[colname2] = None

            cdf = np.array(quantiles, dtype=float)
            inds = np.argsort(cdf)
            cdf = cdf[inds]

            for i in range(0, len(data)):

                # Collects the price vals
                vals = data[quantiles].iloc[i].to_numpy(copy=True)
                vals = vals[inds]

                # Calculates the pdf
                pdf_y = cdf[1:]-cdf[0:-1]
                pdf_y = np.concatenate([[cdf[0]], pdf_y])
                pdf_x = 1.0*vals

                # Expected shortfall
                filter_long = np.heaviside(-(pdf_x-entry_prices[i]), 0.5)
                filter_short = np.heaviside((pdf_x-entry_prices[i]),  0.5)
                expected_shortfall_long = np.sum(
                    filter_long*pdf_x*pdf_y) / np.sum(filter_long*pdf_y)
                expected_shortfall_short = np.sum(
                    filter_short*pdf_x*pdf_y) / np.sum(filter_short*pdf_y)
                data.loc[data.index[i], colname1] = expected_shortfall_long
                data.loc[data.index[i], colname2] = expected_shortfall_short

            out = data

        return out
    
def movecol(df, cols_to_move=[], ref_col='', place='After'):
    cols = df.columns.tolist()
    
    
    if place == 'After':
        seg1 = cols[:list(cols).index(ref_col) + 1]
        seg2 = cols_to_move
    if place == 'Before':
        seg1 = cols[:list(cols).index(ref_col)]
        seg2 = cols_to_move + [ref_col]
    seg1 = [i for i in seg1 if i not in seg2]
    seg3 = [i for i in cols if i not in seg1 + seg2]
    
    return(df[seg1 + seg2 + seg3])
        


############################################## Usage

##### Authentication
# %%
if False:    
    apc = ArgusPossibilityCurves(username="user@domain.com", password="your_password")
    apc.authenticate()

    #set update_from_remote to false if you don't want to check for new metadata
    apc.getMetadataCSV(filepath="argus_latest_meta.csv", force_update_from_remote=True)


##### Gets available Possibility Curves
# %%
if False:    
    available_poss_curves = apc.get_available_poss_curves()
    available_poss_curves.sort()
    print("Available possibility curves:")
    print(*available_poss_curves, sep='\n')
    

##### Gets available OBOS levels
# %%
if False:
    available_obos = apc.get_available_obos()
    available_obos.sort()
    print("Available OBOS:")
    print(*available_obos, sep='\n')
    

##### Retrieves PossibilityCurves data
# %%
if False:    
    
    categories = ['Argus Nymex WTI month 1, Daily',
                  'Argus Nymex WTI month 2, Daily',
               'Argus Nymex Heating oil month 1, Daily',
               'Argus Nymex RBOB Gasoline month 1, Daily',
               'Argus Brent month 1, Daily',
               'Argus Brent month 2, Daily',
               'Argus ICE gasoil month 1, Daily']

    #categories = ['Argus Brent month 1, Daily', 
                  #'Argus WTI Houston front month average, Monthly']
    start_date = datetime.date(2024, 1, 15)
    end_date = datetime.date(2024, 1, 30)
    apc_data = apc.getPossibilityCurves(
        start_date=start_date, end_date=end_date, categories=categories)
    print(apc_data)
    print(apc_data.columns)


##### Retrieves OBOS data
# %%
if False: 
    obos = ['Argus Nymex WTI month 1',
            'Argus Brent month 1']
    start_date = datetime.date(2023, 7, 4)
    end_date = datetime.date(2023, 8, 4)
    obos_data = apc.getOBOS(start_date=start_date, end_date=end_date, obos=obos)
    print(obos_data)
    print(obos_data.columns)



##### Calculates statistics
if False:
    categories = ['Argus Brent month 1, Daily']
    start_date = datetime.date(2020, 12, 1)
    end_date = datetime.date(2021, 1, 20)
    apc_data = apc.getPossibilityCurves(start_date=start_date, end_date=end_date, categories=categories)
    data_with_stats = apc.calculate_statistics(data=apc_data)
    cols = ["IQR", "Central Skewness", "Tail Skewness", "Downside Tail Risk",  "Upside Tail Risk"]
    print(data_with_stats[cols])



##### Calculates Expected shortfall
if False:
    categories = ['Argus Brent front month spread, Daily']
    start_date = datetime.date(2021, 1, 1)
    end_date = datetime.date(2021, 1, 14)
    apc_data = apc.getPossibilityCurves(start_date=start_date, end_date=end_date, categories=categories)
    # Let's calculate both at the 0.5 and 0.75 quantile levels
    entry_prices = list(apc_data['0.5'].to_numpy())
    data_with_expected_shortfall = apc.calculate_expected_shortfall(data=apc_data, entry_prices=entry_prices, label="at 0.5 level")
    cols = ['Expected Shortfall (LONG) - at 0.5 level',
            'Expected Shortfall (SHORT) - at 0.5 level']
    print(data_with_expected_shortfall[cols])



##### Calculates Trading signals
if False:
    categories = ['Argus Brent month 1, Daily']
    start_date = datetime.date(2021, 1, 1)
    end_date = datetime.date(2021, 1, 31)
    apc_data = apc.getPossibilityCurves(start_date=start_date, end_date=end_date, categories=categories)
    data_with_trading_signals = apc.calculate_trading_signals(data=apc_data, IQR_window=10, Skew_window=12)
    cols=['IQR', 'IQR Moving Average', 'Central Skewness', 'Central Skewness Moving Average', 'Signal IQR', 'Signal IQR-Skewness']

    print(data_with_trading_signals[cols])

