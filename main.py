#!/usr/bin/python
# -*- coding: cp1252 -*-
from mechanize import *
import os
import ftplib

class Sync:
    def __init__(self, username,password):
        self.username = username
        self.password = password
        self.courses = {}
        self.sel_courses={}
        self.br=Browser()
        self.br.set_handle_equiv(True)
        #self.br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        self.logged1=False
        self.logged2=False
        try:
            self.log_moodle()
        except : None
        try:
            self.log_bighome()
        except: None

    def log_moodle(self):
        self.br.open('http://moodle.iitb.ac.in')
        print self.br.title()
        self.br.select_form(nr=1)
        self.br.form.controls[0].readonly = False # make server_id writeable
        self.br.form.controls[1].readonly = False # make server_id writeable
        self.br["username"] = self.username
        self.br["password"] = self.password
        self.br.submit()
        if not "Login" in self.br.title():
            self.logged1=True
            print "Moodle Logged In"
            
    def islog1(self):
        if not "Login" in self.br.title():
            print "not logged in"
            return True
        else : return False
        
    def islog2(self):
        try :
            self.s.nlst()
            return True
        except : return False

    def log_bighome(self):
        self.s=ftplib.FTP('bighome.iitb.ac.in' , self.username , self.password)
        if self.islog2():
            self.logged2=True
            print "Bighome Logged In"
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def getfolder(self, name, flink ):
        print 'into folder   : ', name
        try: 
            localstoredfiles=os.listdir(name)   #LIST OF FILES/FOLDERS IN LOCAL COMP IN CURR DIR
            os.chdir(name)
        except :
            os.mkdir(name)
            localstoredfiles=os.listdir(name)
            os.chdir(name)
        print 'made folder in comp'

        try :
            self.s.cwd(name)
        except :
            self.s.mkd(name)
            self.s.cwd(name)
        print 'made folder in bighome'

        
        #print "uell  ",response.geturl()
        try:
            bigstoredfiles=self.s.nlst()  #LIST OF FILES/FOLDERS IN BIGHOME IN CURR DIR
            print "link for main folder", flink.url
            response=self.br.open(flink.url)
            print 'link open', self.br.title() ,self.br.geturl()
        except :
            print 'cant open link :::       ' , flink.url
            
        print 'to download :'
        for link in self.br.links():
            if (link.url != '#maincontent'):
                print link.url
                
                if "mod/folder/view" in link.url:  #NOTE:  THIS ASSUMPTION MAY OR MAY NOT BE CORRCT AS THERE IS NO  FOLDER IN FOLDER IN test MOODLE ACCNT
                    print "folder into folder under construction"
                else :
                    print 'trying to download file'
                    #response=self.br.open(link.url)     UNABLE TO DO THIS IF LINK IS THAT OF A  FILE 
                    if 'mod_folder/content' in link.url:
                        print 'accessing a file in folder  '
                        ftype='properfile'  #with direct download link
                        filename=link.url.rsplit('/',1)[1].rsplit('?',1)[0]    # if url is of 'xyzfksjfkj/helper.tar.gz?fart'
                        #print 'splitted'
                        if filename not in localstoredfiles:
                            b=self.br.retrieve(link.url, filename)
                            print 'uploaded ' ,filename,  '  :  '
                        if filename not in bigstoredfiles:
                            f= open(filename,'rb')
                            self.s.storbinary('STOR '+ filename, f)
                            print 'uploaded ' ,filename,  '  :  '  
                            f.close
                    else :
                        print ' >>      >>>>    >   >   > it was not a file '
            else:
                print "            +++++++++++ BAD LINK " ,link   

        os.chdir('..')
        self.s.cwd('..')
        print 'moved back ..'
                   
    def getpdf(self, name, link , localstoredfiles,bigstoredfiles):
        #print 'sAF enter'
        assert self.br.viewing_html() 
        #print 'sAF'
        
        try:
            l2=self.s.nlst()

            self.br.open(link.url)
            print 'link open'
        except :
            print 'cant open link :::       ' , link.url
            
        #print 'to download :'
        #for x in self.br.links():
         #   if '[IMG]' in x.text :
          #      print x.text.split('[IMG]')[1][1:].strip()

        for link in self.br.links():
            #response= self.br.open(link.url)
            if ".pdf" in link.url:
               filename=link.url.rsplit('/',1)[1].rsplit('?',1)[0]
               response=self.br.open(link.url)
               #print "response's url is ", response.geturl()
               #print "actual url is",link.url
               
               if filename not in localstoredfiles:
                   b=self.br.retrieve(response.geturl(), filename)
                   print 'downloaded' ,filename
               if filename not in bigstoredfiles:
                   f= open(filename,'rb')
                   self.s.storbinary('STOR '+ filename, f)
                   print 'uploaded ' ,filename
                   f.close

                    
    #only for pdf files and that too here folder does not change

            
    def listCourses(self):
        #to be used immediately after log_moodle and log_bighome
        self.courses={}
        
        check = ('title', 'Click to enter this course')
        for link in self.br.links():
            if check in link.attrs:
                text = link.text.split(':')
                self.courses[text[0].strip().replace(' ','')] = link
        return self.courses.keys()
            
############################################################################################################################################
    def setup(self, templist_sel):  #  list of sel 

        #takes input of list ofselected courses names(only) and stores in form
        #of dictionary with (name ,link) tuple using self.courses
        self.sel_courses={}
        

        for x in templist_sel:
            try :
                self.sel_courses[x]=self.courses[x]
            except : None
            
        #in users computer change dir to 'username' on Desktop
        
        try :
            print "destination"
            print os.getcwd()
            localtemp=os.listdir(self.username)
            os.chdir(self.username)
        except:
            print "destination"
            print os.getcwd()
            os.mkdir(self.username)
            localtemp=os.listdir(self.username)
            os.chdir(self.username)
        #then creates course folders in 'username' directory in computer
        for c in self.sel_courses:
            if c not in localtemp:
                os.mkdir(c) 
        
        #in bighome changes dir to 'username' (if not  first create)
        try: 
            self.s.cwd(self.username)
        except : 
            self.s.mkd(self.username)
            self.s.cwd(self.username)
            
         #then creates course folders in 'username' directory
        print "\n making folders in bighome ..... ... ..."
        bigtemp=self.s.nlst()

        for c in self.sel_courses:
            if c not in bigtemp:
                self.s.mkd(c)
        print 'initial setup complete now will start syncing'
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def syncnow(self):
        for course in self.sel_courses:
            self.br.open(self.sel_courses[course].url)
            assert self.br.viewing_html()
            

            localstoredfiles=os.listdir(course)   #computer
            os.chdir(course)                              #computer

            self.s.cwd(course)         #bighome
            bigstoredfiles=self.s.nlst()      #names of files with extension    AND folders
            
            filelist={}
            folderlist={}   
            for link in self.br.links():
                #print link.url
                if "mod/resource/view" in link.url:    ######TRUE ONLY FOR FILE TYPE OF RESOURCES
                    name=link.text.replace('[IMG]','')
                    filelist[name] = link
                if "mod/folder/view" in link.url:    ######TRUE ONLY FOR FOLDER TYPE OF RESOURCES
                    #print "saw a folder", link.text
                    name=link.text.replace('[IMG]','').replace(' ','').replace(':','_').replace('Folder','')
                    folderlist[name] = link
                

            for afile in filelist:
                try:
                    response= self.br.open(filelist[afile].url)
                    try :
                        assert self.br.viewing_html()         #if passes means it was a folder not a file
                        ftype='pdf'
                    except :
                        ftype='File'

                        
                    if ftype=='File':     
                        try :
                            print 'into file'
                            filename=response.geturl().rsplit('/',1)[1].rsplit('?',1)[0]    # if url is of 'xyzfksjfkj/helper.tar.gz?fart'
                            if filename not in localstoredfiles:
                                b=self.br.retrieve(response.geturl(), filename)
                                print 'uploaded ' ,filename,  '  :  ',response.geturl()
                            if filename not in bigstoredfiles:
                                f= open(filename,'rb')
                                self.s.storbinary('STOR '+ filename, f)
                                print 'uploaded ' ,filename,  '  :  ',response.geturl()   
                                f.close
                        except:
                            print 'download/ upload fail for',afile
                    else:
                        try:
                            print 'for a pdf file'           #VIMP
                            self.getpdf(afile,filelist[afile],localstoredfiles,bigstoredfiles) #now trying only for pdf files  #call getfolder func with name and link                  
                        except:
                            print 'cant get the pdf file',afile
                except:
                    print 'cant open link for ', afile


            #NOW CODE FOR FLDERS IN THE COURSE PAGE
            
            for afolder in folderlist:
                try :
                    print folderlist[afolder].url
                    self.br.open(folderlist[afolder].url)
                    #print 'openable'
                    self.getfolder(afolder, folderlist[afolder])
                    #for x in self.br.links():
                        #print "               ---------", x.url
                except :
                    print 'wrong link' , folderlist[afolder]
            
                    
            
            
                
            print 'sync completed for' , course
            print os.getcwd()
            os.chdir('..')
            self.s.cwd('..')        

##                    os.chdir('c:\\users\\sachin\\Desktop\\Sync\\v3')

            
            
            

        
        
        
            
            
            
        
        
        

