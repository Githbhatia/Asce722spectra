from tkinter import *
from tkinter import messagebox
import certifi
import ssl
import geopy.geocoders
from geopy.geocoders import Nominatim
import urllib.request as ur
import urllib.error
import json as js
import numpy as np
import matplotlib.pyplot as plt
#import folium
import webbrowser

class Root(Tk):
    def __init__(self):
        super().__init__()
        self.geometry('370x320')
        self.title("ASCE 7-22 Seismic Parameters")
        
        self.menubar = Menu()
        self.menubar.add_command(label="Quit", command=self.quit)

        self.help = Menu(self.menubar, tearoff=0)  
        self.help.add_command(label="About", command=self.about)  
        self.menubar.add_cascade(label="Help", menu=self.help)
        
        self.config(menu =self.menubar)
        self.grid_columnconfigure(1, minsize=200)
        self.title_label = Label(text="ASCE7-22 Seismic Parameter Input").grid(row=0,column=0, columnspan = 2,sticky="ew")
        
        
        self.label_Title = Label(text="Title").grid(row=1,column=0)
        self.entry_Title  = Entry()
        self.entry_Title.grid(row=1,column=1,sticky="ew")
        self.entry_Title.insert(0,"My Site")

        self.title_SWVel = Label(text="Either enter Shear Wave Velocity or pick Site Class").grid(row=2,column=0, columnspan = 2)
        self.title_SWVel2 = Label(text="(Shear Wave Velocity will be used when entered)").grid(row=3,column=0, columnspan = 2)
        self.label_SWVel = Label(text="Shear Wave Velocity (ft/s)").grid(row=4,column=0)
        self.entry_SWVel  = Entry()
        self.entry_SWVel.grid(row=4,column=1,sticky="ew")
        self.entry_SWVel.insert(0,"")

        SiteClassList=["A","B","BC","C","CD","D","DE","E","F"]
        self.SelectedSiteClass=StringVar()
        self.SelectedSiteClass.set("CD")
        self.label_SiteClass = Label(text="Site Class").grid(row=5,column=0)
        self.list_SiteClass = OptionMenu(self, self.SelectedSiteClass,*SiteClassList)
        self.list_SiteClass.grid(row=5,column=1,sticky="ew")

        RiskCategoryList=["I","II","III","IV"]
        self.SelectedRiskCategory =StringVar()
        self.SelectedRiskCategory.set("IV")
        self.label_RiskCategory = Label(text="Risk Category").grid(row=6,column=0)
        self.list_RiskCategory = OptionMenu(self,self.SelectedRiskCategory,*RiskCategoryList)
        self.list_RiskCategory.grid(row=6,column=1,sticky="ew")

        self.title_label = Label(text="Either provide Address or Lat/Long Pair (leave Address blank)").grid(row=7,column=0, columnspan = 2)

        self.label_Address = Label(text="Address").grid(row=8,column=0)
        self.entry_Address = Entry()
        self.entry_Address.grid(row=8,column=1,sticky="ew")
        self.entry_Address.insert(0,"")
  
        self.label_Latitude = Label(text="Latitude").grid(row=9,column=0)
        self.entry_Latitude = Entry()
        self.entry_Latitude.grid(row=9,column=1,sticky="ew")
        self.entry_Latitude.insert(0,"38")

        self.label_Longitude = Label(text="Longitude").grid(row=10,column=0)
        self.entry_Longitude  = Entry()
        self.entry_Longitude.grid(row=10,column=1,sticky="ew")
        self.entry_Longitude.insert(0,"-121")

        self.SaveJson=IntVar()
        self.checkbutton_SaveJson=Checkbutton(self, text="Save Json", variable=self.SaveJson)
        self.checkbutton_SaveJson.grid(row=11,column=0,sticky="ew")

        self.OpenMap=IntVar(value= 1)
        self.checkbutton_OpenMap=Checkbutton(self, text="Open Map", variable=self.OpenMap)
        self.checkbutton_OpenMap.grid(row=11,column=1,sticky="ew")

        self.button = Button( text="Compute", bg='white', height=2, width=20, command=self.onclick).grid(row=12,column=0)

        
    def onclick(self):
        if str(self.entry_SWVel.get()) != "":
            try:
                shearwavevel = float(self.entry_SWVel.get())
            except ValueError:
                messagebox.showinfo("Invalid Shear Wave Velocity", "Enter shear wave velocity in ft/sec and try again")
                return
            if shearwavevel==0:
                messagebox.showinfo("Invalid Shear Wave Velocity", "Enter a non-zero shear wave velocity in ft/sec and try again")
                return
            shearwavevellimits = [('F',0.0),('E',500.0),('DE',700.0),('D',1000.0),('CD',1450.0),('C',2100.0),('BC',3000.0),('B',5000.0),('A',1000000.0)]
            index = 0
            for a, b in shearwavevellimits:
                if shearwavevel <= b:
                    sitecl = a
                    break
        else:
            sitecl = str(self.SelectedSiteClass.get())
        self.SelectedSiteClass.set(sitecl)

        
        ctx = ssl._create_unverified_context(cafile=certifi.where())
        geopy.geocoders.options.default_ssl_context = ctx
        geolocator = Nominatim(user_agent="ASCE722MultiPeriodResponseSpectra", scheme='https')
        sitetitle = str(self.entry_Title.get())
        riskct = str(self.SelectedRiskCategory.get())
        address = str(self.entry_Address.get())

        if address =="":
            lat = str(self.entry_Latitude.get())
            longt= str(self.entry_Longitude.get())
            location = geolocator.reverse(lat + " ," + longt)
            address = str(location.address)
            self.entry_Address.delete(0,"end")
            self.entry_Address.insert(0, address)
        else:
            location = geolocator.geocode(address)
            if (location != None):
                lat = str(location.latitude)
                longt = str(location.longitude)
                self.entry_Latitude.delete(0,"end")
                self.entry_Longitude.delete(0,"end")
                self.entry_Latitude.insert(0,lat)
                self.entry_Longitude.insert(0,longt)
                self.entry_Address.delete(0,"end")
                address = str(location.address)
                self.entry_Address.insert(0, address)
            else:
                messagebox.showinfo("Invalid Address", "Invalid address, revise address and try again")
                return()
            
        #print(location.address)
        #print((location.latitude, location.longitude))

        url = 'https://earthquake.usgs.gov/ws/designmaps/nehrp-2020.json?latitude='+ lat + '&longitude=' + longt +'&riskCategory='+ riskct +'&siteClass=' + sitecl + '&title=Example'


        try:
            response = ur.urlopen(url)
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
                return()
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
                return()

        self.geometry('370x650')     
        rdata = js.loads(response.read())
        if self.SaveJson.get() == 1:
            with open("ASCE722.json", "w") as write_file:
                js.dump(rdata, write_file)

        output = 'Output for Latitude = ' + str(lat) + ' Longitude = ' + str(longt)
        t = rdata["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
        s = rdata["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]

        t2 = rdata["response"]["data"]["twoPeriodDesignSpectrum"]["periods"]
        s2 = rdata["response"]["data"]["twoPeriodDesignSpectrum"]["ordinates"]
            
        tmce = rdata["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
        smce = rdata["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]

        tmce2 = rdata["response"]["data"]["twoPeriodMCErSpectrum"]["periods"]
        smce2 = rdata["response"]["data"]["twoPeriodMCErSpectrum"]["ordinates"]
            
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(121)
        ax.set_xlabel('Period')
        ax.set_title(sitetitle + " Design Spectrum")
        ax.plot(t, s, label="Multiperiod Design Spectrum", color='Red', linewidth=1.0)
        ax.plot(t2, s2, label="2-Period Design Spectrum", color='Green', linewidth=1.0)
        ax.set_xlim([0, 5])
        ax.legend()

        ax2 = fig.add_subplot(122)
        ax2.set_xlabel('Period')
        ax2.set_title(sitetitle + " MCE Spectrum")
        ax2.plot(tmce, smce, label="MCE Multiperiod Spectrum", color='Blue', linewidth=1.0)
        ax2.plot(tmce2, smce2, label="MCE 2-Period  Spectrum", color='Green', linewidth=1.0)
        ax2.set_xlim([0, 5])
        ax2.legend()
        
        p = rdata["response"]["data"]
        self.title_label = Label(text="ASCE7-22 Seismic Parameter Output").grid(row=14,column=0, columnspan = 2)
        index = 0
        for key, value in p.items():
            if index <= 11:
                Label(self, text=str(key), relief = "sunken", width= 20).grid(column=0, row=index+15)
                Label(self, text=str(value), relief = "sunken", width = 20).grid(column=1, row=index+15)
            index += 1
 

        self.button2 = Button(self, text="Quit", bg='red', height=2, width=20, command=lambda:self.onclick2(plt)).grid(row=28,column=1)
        self.button3 = Button(self, text="Write File", bg='green', height=2, width=20,command= lambda:self.mywritefile(rdata, plt, sitecl)).grid(row=28,column=0)

        if self.OpenMap.get()==1:
 #           map = folium.Map(location=[float(lat),float(longt)],zoom_start=12)
 #           folium.Marker([float(lat),float(longt)], popup="Location").add_to(map)
 #           map.save("mymap.html")
 #           webbrowser.open("mymap.html")
            webbrowser.open('http://www.google.com/maps/place/'+ lat +','+longt+'/@'+ lat +','+longt+',12z', new=2)
        plt.show()

    def quit(self):
        self.destroy()
        
    def onclick2(self, plt):
        plt.close('all')
        self.destroy()

    def mywritefile(self, ldata, plt, sitecl):
        sitetitle = str(self.entry_Title.get())
        riskct = str(self.SelectedRiskCategory.get())
        address = str(self.entry_Address.get())
        lat = str(self.entry_Latitude.get())
        longt= str(self.entry_Longitude.get())
        index = 0
        p = ldata["response"]["data"]
        t = ldata["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
        s = ldata["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]
        tmce = ldata["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
        smce = ldata["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
        with open('ASCE722.txt', 'w') as f:
            f.write("Data source is USGS (NEHRP 2020 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy.\n")
            f.write("Use of the output of this program does not imply approval by the governing building code bodies responsible for building code approval and interpretation for the building site described by latitude/longitude location.\n")
            f.write("Written by HXB\n \n \n")
            f.write(sitetitle + "\n" + address + "\n")
            f.write("The location is " + lat + ", " + longt + " with Site Class " + sitecl + " and Risk Category "+ riskct + "\n")
            if str(self.entry_SWVel.get()) != "":
                f.write("Site Class based on a shear wave velocity of " + str(self.entry_SWVel.get()) + "ft/s\n")
            for key, value in p.items():
                if index <= 11:
                    f.write(str(key)+ ", " + str(value)+"\n")     
                index += 1
            
            f.write("MultiPeriodDesignSpectrum\n")
            index = len(t)
            j = 0
            while j < index:
                f.write(str(t[j])+ ", " + str(s[j])+"\n")
                j+= 1
            f.write("MultiPeriodMCErSpectrum\n")
            index = len(tmce)
            j = 0
            while j < index:
                f.write(str(tmce[j])+ ", " + str(smce[j])+"\n")
                j+= 1
        plt.savefig('spectra.png')


    def about(self):
        messagebox.showinfo('ASCE722', 'Get the Multi-period response spectrum for a site for use with ASCE 7-22.\n\nFree to use.\n\
Data source is USGS (NEHRP 2020 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy. \
Use of the output of this program does not imply approval by the governing building code bodies responsible for building code \
approval and interpretation for the building site described by latitude/longitude location.\n \n\
Written by HXB')


root = Root()
root.mainloop()


