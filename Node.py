
class NodeElement(object):

    def __init__(self, node,root):
        self.tool_id = node.attrib['ToolID']
        self.plugin = node.find('GuiSettings').attrib.get('Plugin')
        self.x_pos = float(node.find('GuiSettings').find('Position').attrib['x'])
        self.y_pos = float(node.find('GuiSettings').find('Position').attrib['y'])
        self.tool = self.plugin.split('.')[-1] if self.plugin else None
        self.description = None
        self.ljoin_fields = []
        self.rjoin_fields = []
        self.select_fields = []
        
        self.query = ""
        self.sparkquery = ""
        if self.plugin == 'AlteryxBasePluginsGui.Join.Join':
            join_data = node \
                .find('Properties') \
                .find('Configuration') \
                .findall('JoinInfo')
            ljoin_data = join_data[0]
            rjoin_data = join_data[1]
            self.ljoin_fields = []
            lj =""
            rj=""
            for field in ljoin_data.findall('Field'):
                self.ljoin_fields.append(field.attrib['field'])
                lj = lj + "," + field.attrib['field']
            self.rjoin_fields = []
            for field in rjoin_data.findall('Field'):
                self.rjoin_fields.append(field.attrib['field'])
                rj = rj + "," + field.attrib['field']
            joinstr =""
            for i in range(0,len(self.ljoin_fields)) :
                joinstr=joinstr+"ldfs(\""+self.ljoin_fields[i] + "\")===rdfs(\""+self.rjoin_fields[i]+ "\"),"
                

            self.query = "select * from " + lj + rj
            self.sparkquery = "val df"+self.tool_id+" = ldfs.join(rdfs," +joinstr[:-1] + ",inner)"

        

        elif self.plugin == 'AlteryxGuiToolkit.ToolContainer.ToolContainer':
            self.description = node \
                .find('Properties') \
                .find('Configuration') \
                .find('Caption').text

        

        elif self.plugin == 'AlteryxBasePluginsGui.AlteryxSelect.AlteryxSelect':
            self.select_fields = node \
                .find('Properties') \
                .find('Configuration') \
                .find('SelectFields') \
                .findall('SelectField')
            self.select_fields = [field.attrib for field in self.select_fields]
            for e in self.select_fields:
                if(e['selected']=='True'):
                    rename = ""
                    if("rename" in e):
                        rename = e['rename']
                        self.query =self.query+ e['field']+ " as "+rename +","
                        self.sparkquery = self.sparkquery + "\"" + e['field']+ " as "+rename+ "\"" +","
                    else:
                        self.query =self.query+ e['field'] +","
                        self.sparkquery = self.sparkquery + "\"" + e['field']+ "\""  +","

            self.sparkquery = "val df"+self.tool_id+" = df.selectExpr(" + self.sparkquery[:-1] + ")"


        


        elif self.plugin == 'AlteryxBasePluginsGui.Formula.Formula':
            self.sparkquery = node \
                .find('Properties') \
                .find('Configuration') \
                .find('FormulaFields') \
                .findall('FormulaField')
            self.sparkquery = [field.attrib for field in self.sparkquery]
            filt = ""
            for e in self.sparkquery:
                if 'IF' in e['expression']:
                    filt = filt + ".withColumn(\""+e['field']+"\",expr(\""+e['expression'].replace('\"', '\'').replace('ENDIF'," end ").replace('ELSEIF'," when ").replace('IF',"case when ").replace('[',' ').replace(']',' ') + "\"))"
                elif (e['type']=='V_WString'):
                    filt = filt + ".withColumn(\""+e['field']+"\",lit(\""+e['expression'] + "\"))"
                else:
                    filt = filt + ".withColumn(\"" + e['field']+"\",lit("+e['expression'] + "))"

            self.sparkquery = "val df"+self.tool_id+" = df"+filt.replace('\n', ' ')

        # else:
        #     self.select_fields = None

        elif self.plugin == 'AlteryxBasePluginsGui.AppendFields.AppendFields':
            # self.sparkquery = node \
            #     .find('Properties') \
            #     .find('Configuration') \
            #     .find('FormulaFields') \
            #     .findall('FormulaField')
            # self.sparkquery = [field.attrib for field in self.sparkquery]
            filt = ""
            # for e in self.sparkquery:
            #     if(e['type']=='V_WString'):
            #         filt = filt + ".withColumn("+e['field']+",lit(\""+e['expression'] + "\"))"
            #     else:
            #         filt = filt + ".withColumn(" + e['field']+",lit("+e['expression'] + "))"

            self.sparkquery = "val df"+self.tool_id+" = df"+filt

        # else:
        #     self.select_fields = None

        elif self.plugin == 'AlteryxBasePluginsGui.Unique.Unique':
            self.unique_fields = node \
                .find('Properties') \
                .find('Configuration') \
                .find('UniqueFields') \
                .findall('Field')
            self.unique_fields = [field.attrib for field in self.unique_fields]
            for e in self.unique_fields:
                self.sparkquery = self.sparkquery + "\"" + e['field']+ "\""  +","

            self.sparkquery = "val df"+self.tool_id+" = df.dropDuplicates(" + self.sparkquery[:-1] + ")"

        # else:
        #     self.select_fields = None
        elif self.plugin == 'AlteryxBasePluginsGui.Union.Union':

            self.sparkquery = "val df"+self.tool_id+" = ldfs.UnionByName(rdfs)"


        elif self.plugin == 'AlteryxBasePluginsGui.Sort.Sort':
            self.sort_fields = node \
                .find('Properties') \
                .find('Configuration') \
                .find('SortInfo') \
                .findall('Field')
            self.sort_fields = [field.attrib for field in self.sort_fields]
            for e in self.sort_fields:
                if(e['order']=='Ascending'):
                    self.sparkquery = self.sparkquery + "\"" + e['field']+ "\""  +","
                else:
                    self.sparkquery = self.sparkquery + "desc(\"" + e['field']+ "\")"  +","


            self.sparkquery = "val df"+self.tool_id+" = df.orderBy(" + self.sparkquery[:-1] + ")"


        elif self.plugin == 'AlteryxBasePluginsGui.Filter.Filter':
            self.filter_fields = node \
                .find('Properties') \
                .find('Annotation') \
                .find('DefaultAnnotationText').text

            self.sparkquery = "val df"+self.tool_id+" = df.where(\"" + self.filter_fields+ "\")"

        # else:
        #     self.select_fields = None



        elif self.plugin == 'AlteryxBasePluginsGui.DbFileOutput.DbFileOutput':
            self.sparkquery = "df.write.format().save()"
        
        elif self.plugin == 'AlteryxBasePluginsGui.DbFileInput.DbFileInput':
            self.sparkquery = "val df"+self.tool_id +"= spark.read.format()"



        elif (not self.plugin) or (self.plugin == 'AlteryxGuiToolkit.ToolContainer.ToolContainer' and node.find('Properties').find('Configuration').find('Caption').text == 'Delta tool - DO NOT MODIFY'):
            self.delta =  node \
                .find('Properties') \
                .find('Configuration') \
                .findall('Value')
            c=0
            self.deltaquery=""
            for field in self.delta:
                print(field.text)
                if c==0:
                    for m in field.text.split(","):
                        if(m.endswith("True") and c==0):
                            print(m.split("=")[0])
                            self.deltaquery = self.deltaquery+"\""+m.split("=")[0] +"\","
                    self.sparkquery = "val df"+self.tool_id +"_new=ldfs.as(\"a\").join(rdfs.as(\"b\"), Seq("  +  self.deltaquery[:-1] +"),\"left anti\")\n"
                    self.sparkquery =  self.sparkquery  + "val df"+self.tool_id +"_delete=rdfs.as(\"a\").join(ldfs.as(\"b\"), Seq("  +  self.deltaquery[:-1] +"),\"left anti\")\n"
                    self.sparkquery = self.sparkquery  + "\n val df"+self.tool_id +"_change=ldfs.as(\"a\").join(rdfs.as(\"b\"), Seq("  +  self.deltaquery[:-1] +"),\"inner\")"
                    c=1
                else:
                    self.deltaquery=""
                    for m in field.text.split(","):
                        if(m.endswith("True") and c==1):
                            self.deltaquery =  self.deltaquery+"coalesce(col(\"a."+m.split("=")[0] +"\"), lit(\"\"))=!= coalesce(col(\"b."+m.split("=")[0] +"\"), lit(\"\")) or "
                    self.sparkquery = self.sparkquery +".where("+ self.deltaquery[:-3]+")"

        
        else:
            self.ljoin_fields = None
            self.rjoin_fields = None
            self.select_fields = None
            try:
                self.description = node \
                    .find('Properties') \
                    .find('Annotation') \
                    .find('DefaultAnnotationText').text
            except:
                self.description = None





        self.description = self.description.replace('\n', ' ') if self.description else None
        
        
        for connection in root.find('Connections').iter('Connection'):
             dest = connection.find('Destination').attrib.get('ToolID')
             if(dest==self.tool_id):
                 origin = connection.find('Origin').attrib.get('ToolID')
                 if(origin and connection.find('Destination').attrib.get('Connection')=='Left'):
                     print("1origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('ldfs', 'df'+origin) if self.sparkquery else None
                 if(origin and connection.find('Destination').attrib.get('Connection')=='Right'):
                     print("2origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('rdfs', 'df'+origin) if self.sparkquery else None
                 if(origin and connection.find('Destination').attrib.get('Connection')=='New Records'):
                     print("3origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('ldfs', 'df'+origin+'_new') if self.sparkquery else None
                 if(origin and connection.find('Destination').attrib.get('Connection')=='Changed Records'):
                     print("4origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('rdfs', 'df'+origin+'_change') if self.sparkquery else None
                 if(origin and connection.find('Destination').attrib.get('Connection')=='New Data Stream'):
                     print("5origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('ldfs', 'df'+origin) if self.sparkquery else None
                 if(origin and connection.find('Destination').attrib.get('Connection')=='Old Data Stream'):
                     print("6origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('rdfs', 'df'+origin) if self.sparkquery else None
                 if(origin and connection.find('Origin').attrib.get('Connection')=='New Records'):
                     print("7origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('df.', 'df'+origin+'_new.') if self.sparkquery else None
                 if(origin and connection.find('Origin').attrib.get('Connection')=='Changed Records'):
                     print("8origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('df.', 'df'+origin+'_change.') if self.sparkquery else None
                 if(origin and connection.attrib.get('name')=='#1'):
                     print("1origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('ldfs', 'df'+origin) if self.sparkquery else None
                 if(origin and connection.attrib.get('name')=='#2'):
                     print("2origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('rdfs', 'df'+origin) if self.sparkquery else None
                 if(origin):
                     print("9origin="+origin+"dest = "+dest) 
                     self.sparkquery = self.sparkquery.replace('df.', 'df'+origin+'.') if self.sparkquery else None
                 



        

        self.data = {
            'Tool ID': self.tool_id,
            'Plugin': self.plugin,
            'Tool': self.tool,
            'Description': self.description,
            'x': self.x_pos,
            'y': self.y_pos,
            'Left Join Fields': self.ljoin_fields,
            'Right Join Fields': self.rjoin_fields,
            'Select Fields': self.select_fields,
            # 'Query':  self.query.replace("\"\"","\"").replace("\"v","v"),
            'Spark Query':self.sparkquery
        }
