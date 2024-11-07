from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import numpy as np
import certifi
import ssl
import geopy.geocoders
from geopy.geocoders import Nominatim
import urllib.request as ur
import json as js
import matplotlib.pyplot as plt
#import folium
import webbrowser


class Root(Tk):
    def __init__(self):
        super().__init__()
        #print(certifi.where())
        global rr
        self.geometry('370x385')
        self.title("ASCE 7-22 Seismic Parameters")
        
        self.menubar = Menu()
        self.menubar.add_command(label="Quit", command=self.quit)
        self.help = Menu(self.menubar, tearoff=0)  
        self.help.add_command(label="About", command=self.about)  
        self.menubar.add_cascade(label="Help", menu=self.help)

        rr=0
        self.config(menu =self.menubar)
        self.grid_columnconfigure(1, minsize=200)
        self.title_label = Label(text="ASCE7-22 Seismic Parameter Input").grid(row=rr,column=0, columnspan = 2,sticky="ew"); rr+=1
        
        
        self.label_Title = Label(text="Title").grid(row=1,column=0)
        self.entry_Title  = Entry()
        self.entry_Title.grid(row=rr,column=1,sticky="ew"); rr+=1
        self.entry_Title.insert(0,"My Site")

        self.title_SWVel = Label(text="Either enter Shear Wave Velocity or pick Site Class").grid(row=rr,column=0, columnspan = 2); rr+=1
        self.title_SWVel2 = Label(text="(Shear Wave Velocity will be used when entered)").grid(row=rr,column=0, columnspan = 2); rr+=1
        self.label_SWVel = Label(text="Shear Wave Velocity (ft/s)").grid(row=rr,column=0)
        self.entry_SWVel  = Entry()
        self.entry_SWVel.grid(row=rr,column=1,sticky="ew"); rr+=1
        self.entry_SWVel.insert(0,"")

        self.estSWVel=IntVar()
        self.checkbutton_estSWVel=Checkbutton(self, text="Estimated Shear Wave Velocity?", variable=self.estSWVel)
        self.checkbutton_estSWVel.grid(row=rr,column=0, columnspan = 2,sticky="ew"); rr+=1

        SiteClassList=["A","B","BC","C","CD","D","DE","E", "Default"]
        self.SelectedSiteClass=StringVar()
        self.SelectedSiteClass.set("CD")
        self.label_SiteClass = Label(text="Site Class").grid(row=rr,column=0)
        self.list_SiteClass = OptionMenu(self, self.SelectedSiteClass,*SiteClassList)
        self.list_SiteClass.grid(row=rr,column=1,sticky="ew"); rr+=1

        RiskCategoryList=["I","II","III","IV"]
        self.SelectedRiskCategory =StringVar()
        self.SelectedRiskCategory.set("IV")
        self.label_RiskCategory = Label(text="Risk Category").grid(row=rr,column=0)
        self.list_RiskCategory = OptionMenu(self,self.SelectedRiskCategory,*RiskCategoryList)
        self.list_RiskCategory.grid(row=rr,column=1,sticky="ew"); rr+=1

        self.title_label = Label(text="Either provide Address or Lat/Long Pair (leave Address blank)").grid(row=rr,column=0, columnspan = 2); rr+=1

        self.label_Address = Label(text="Address").grid(row=rr,column=0)
        self.entry_Address = Entry()
        self.entry_Address.grid(row=rr,column=1,sticky="ew"); rr+=1
        self.entry_Address.insert(0,"")
  
        self.label_Latitude = Label(text="Latitude").grid(row=rr,column=0)
        self.entry_Latitude = Entry()
        self.entry_Latitude.grid(row=rr,column=1,sticky="ew"); rr+=1
        self.entry_Latitude.insert(0,"38")

        self.label_Longitude = Label(text="Longitude").grid(row=rr,column=0)
        self.entry_Longitude  = Entry()
        self.entry_Longitude.grid(row=rr,column=1,sticky="ew"); rr+=1
        self.entry_Longitude.insert(0,"-121")

        self.SaveJson=IntVar()
        self.checkbutton_SaveJson=Checkbutton(self, text="Save Json", variable=self.SaveJson)
        self.checkbutton_SaveJson.grid(row=rr,column=0,sticky="ew")

        self.OpenMap=IntVar(value= 1)
        self.checkbutton_OpenMap=Checkbutton(self, text="Open Map", variable=self.OpenMap)
        self.checkbutton_OpenMap.grid(row=rr,column=1,sticky="ew"); rr+=1

        self.locVariation=IntVar()
        self.checkbutton_locVariation=Checkbutton(self, text="Check Local Variation of SDS and SD1", variable=self.locVariation)
        self.checkbutton_locVariation.grid(row=rr,column=0,columnspan = 2); rr+=1

        self.progress = ttk.Progressbar(self,orient='horizontal',mode="indeterminate", length= 200)
        self.progress.grid(row=rr,column=0,columnspan = 2); rr+=1

        self.button = Button( text="Compute", bg='white', height=2, width=20, command=self.onclick).grid(row=rr,column=0)

        
    def onclick(self):
        self.progress.start()
        global rr
        rr=22
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
            centershearwave = [('E',500.0),('DE',600.0),('D',849.0),('CD',1200.0),('C',1732.0),('BC',2500.0),('B',3536.0),('A',1000000.0)]
            index = 0
            for a, b in shearwavevellimits:
                if shearwavevel <= b:
                    sitecl = a
                    break
            prev =0
            for a, b in centershearwave:
                if shearwavevel > b:
                    sitecll = a
                    prev = b
            if shearwavevel <= 500.0:
                sitecll = "E"
                    
            for a, b in centershearwave:
                if shearwavevel <= b:
                    siteclu = a
                    siteclBMultp = (shearwavevel - prev)/(b- prev)
                    break
                    
            if self.estSWVel.get()==1:
                for a, b in shearwavevellimits:
                    if shearwavevel/1.3 <= b:
                        sitecll = a
                        break
                for a, b in shearwavevellimits:
                    if shearwavevel*1.3 <= b:
                        siteclu = a
                        break
            self.SelectedSiteClass.set(sitecl)     
        elif str(self.SelectedSiteClass.get())=="Default":
            sitecl = "CD"
            siteclu = "C"
            sitecll = "D"
        else:
            sitecl = str(self.SelectedSiteClass.get())
        if sitecl == 'F': 
            messagebox.showinfo("Invalid Shear Wave Velocity", "Site Class F, Requires site response analysis studies")
            return
        
        #print(sitecll+" "+siteclu)
        #print(siteclBMultp)

        
        ctx = ssl.create_default_context(cafile=certifi.where())
        print(certifi.where())
        #ctx = ssl._create_unverified_context()
        geopy.geocoders.options.default_ssl_context = ctx
        geolocator = Nominatim(user_agent="ASCE722Spectra", scheme='https')
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

        url = 'https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?latitude='+ lat + '&longitude=' + longt +'&riskCategory='+ riskct +'&siteClass=' + sitecl + '&title=Example'
       
        if  str(self.entry_SWVel.get()) != "" or str(self.SelectedSiteClass.get())=="Default":
            urll = 'https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?latitude='+ lat + '&longitude=' + longt +'&riskCategory='+ riskct +'&siteClass=' + sitecll + '&title=Example'
            urlu = 'https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?latitude='+ lat + '&longitude=' + longt +'&riskCategory='+ riskct +'&siteClass=' + siteclu + '&title=Example'
            

        try:
            response = ur.urlopen(url)
            if str(self.entry_SWVel.get()) != "" or str(self.SelectedSiteClass.get())=="Default":
                responsel = ur.urlopen(urll)
                responseu = ur.urlopen(urlu)
        except ur.URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
                return()
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
                return()

        self.geometry('370x720')     

        rdata = js.loads(response.read())
        if str(self.entry_SWVel.get()) != "" or str(self.SelectedSiteClass.get())=="Default":           
            rdatal = js.loads(responsel.read())
            rdatau = js.loads(responseu.read())

        if self.SaveJson.get() == 1:
            with open("ASCE722.json", "w") as write_file:
                js.dump(rdata, write_file)
            if str(self.entry_SWVel.get()) != "" or str(self.SelectedSiteClass.get())=="Default":
                with open("ASCE722_lowerbound.json", "w") as write_file:
                    js.dump(rdatal, write_file)
                with open("ASCE722_upperbound.json", "w") as write_file:
                    js.dump(rdatau, write_file)

        output = 'Output for Latitude = ' + str(lat) + ' Longitude = ' + str(longt)
        t = rdata["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
        s = rdata["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]

        t2 = rdata["response"]["data"]["twoPeriodDesignSpectrum"]["periods"]
        s2 = rdata["response"]["data"]["twoPeriodDesignSpectrum"]["ordinates"]
            
        tmce = rdata["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
        smce = rdata["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]



        tmce2 = rdata["response"]["data"]["twoPeriodMCErSpectrum"]["periods"]
        smce2 = rdata["response"]["data"]["twoPeriodMCErSpectrum"]["ordinates"]

        if str(self.entry_SWVel.get()) != "" or str(self.SelectedSiteClass.get())=="Default":    
            tl = rdatal["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
            sl = rdatal["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]
            
            tu = rdatau["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
            su = rdatau["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]

            tmcel = rdatal["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
            smcel = rdatal["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]

            tmceu = rdatau["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
            smceu = rdatau["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]

        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(121)
        ax.set_xlabel('Period')
        ax.set_title(sitetitle + " Design Spectrum")
        ax2 = fig.add_subplot(122)
        ax2.set_xlabel('Period')
        ax2.set_title(sitetitle + " MCE Spectrum")

        if (self.estSWVel.get()==1 and str(self.entry_SWVel.get()) != ""):
            for label in self.grid_slaves():
                if int(label.grid_info()["row"]) > 22:
                    label.grid_forget()
            sg = [max(sl,s,su) for sl,s,su in zip(sl,s,su)]
            ax.plot(t, sl, label="Multiperiod Des Spec lower bound SC= "+ sitecll, color='Red', linewidth=1.0)
            ax.plot(t, s, label="Multiperiod Des Spec SC= " + sitecl, color='Blue', linewidth=1.0)
            ax.plot(t, su, label="Multiperiod Des Spec upper bound SC= "+ siteclu, color='Green', linewidth=1.0)
            ax.plot(t, sg, label="Govering Multiperiod Des Spec", color='Black', linestyle='--', linewidth=2.0)
            ax.set_xlim([0, 5])
            ax.legend()  
            ax.grid()
            smcel = rdatal["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
            smceu = rdatau["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
            smceg = [max(smcel,smce,smceu) for smcel,smce,smceu in zip(smcel,smce,smceu)]
            ax2.plot(tmce, smcel, label="MCE Multiperiod lower bound SC= "+ sitecll, color='Red', linewidth=1.0)
            ax2.plot(tmce, smce, label="MCE Multiperiod Spec SC= " + sitecl, color='Blue', linewidth=1.0)
            ax2.plot(tmce, smceu, label="MCE Multiperiod upper bound SC= "+ siteclu, color='Green', linewidth=1.0)
            ax2.plot(tmce, smceg, label="Govering MCE Multiperiod", color='Black', linestyle='--', linewidth=2.0)
            ax2.set_xlim([0, 5])
            ax2.legend() 
            ax2.grid()
            rr+=1
            self.title_label = Label(text="ASCE7-22 Seismic Parameter Output").grid(row=rr,column=0, columnspan = 2); rr+=1
            self.title_label2 = Label(text="Based on est. shear wave velocity per ASCE 7-22 Section 20.3 and 21.4").grid(row=rr,column=0, columnspan = 2); rr+=1
            sds = 0.9 * max(sg[t.index(0.2):t.index(5.0)])
            sd1min = sg[t.index(1.0)]
            sd1 = 0.0
            if shearwavevel > 1450:
                for i in range(t.index(1.0), t.index(2.0)+1):
                    sd1 = max(0.9*sg[i]*t[i], sd1)
                sd1=max(sd1,sd1min)
            elif shearwavevel <= 1450:
                for i in range(t.index(1.0), t.index(5.0)+1):
                    sd1 = max(0.9*sg[i]*t[i], sd1)
                sd1=max(sd1,sd1min)
            Label(self, text=str("sms"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sds*1.5,3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            Label(self, text=str("sm1"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sd1*1.5,3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            Label(self, text=str("sds"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sds,3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            Label(self, text=str("sd1"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sd1,3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            Label(self, text=str("pga"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sg[0],3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            self.button3 = Button(self, text="Write File", bg='green', height=2, width=20,command= lambda:self.mywritefileEstSV(t, sg, tmce, smceg, sds, sd1, plt, sitecl)).grid(row=rr,column=0)
        elif str(self.SelectedSiteClass.get())=="Default":   
            for label in self.grid_slaves():
                if int(label.grid_info()["row"]) > 22:
                    label.grid_forget()
            sg = [max(sl,s,su) for sl,s,su in zip(sl,s,su)]
            ax.plot(t, sl, label="Multiperiod Des Spec lower bound SC= "+ sitecll, color='Red', linewidth=1.0)
            ax.plot(t, s, label="Multiperiod Des Spec SC= " + sitecl, color='Blue', linewidth=1.0)
            ax.plot(t, su, label="Multiperiod Des Spec upper bound SC= "+ siteclu, color='Green', linewidth=1.0)
            ax.plot(t, sg, label="Govering Multiperiod Des Spec", color='Black', linestyle='--', linewidth=2.0)
            ax.set_xlim([0, 5])
            ax.legend()  
            ax.grid()
            smcel = rdatal["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
            smceu = rdatau["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
            smceg = [max(smcel,smce,smceu) for smcel,smce,smceu in zip(smcel,smce,smceu)]
            ax2.plot(tmce, smcel, label="MCE Multiperiod lower bound SC= "+ sitecll, color='Red', linewidth=1.0)
            ax2.plot(tmce, smce, label="MCE Multiperiod Spec SC= " + sitecl, color='Blue', linewidth=1.0)
            ax2.plot(tmce, smceu, label="MCE Multiperiod upper bound SC= "+ siteclu, color='Green', linewidth=1.0)
            ax2.plot(tmce, smceg, label="Govering MCE Multiperiod", color='Black', linestyle='--', linewidth=2.0)
            ax2.set_xlim([0, 5])
            ax2.legend() 
            ax2.grid()
            rr+=1
            self.title_label = Label(text="ASCE7-22 Seismic Parameter Output").grid(row=rr,column=0, columnspan = 2); rr+=1
            self.title_label2 = Label(text="Default = Max of Site Class C, CD, D").grid(row=rr,column=0, columnspan = 2); rr+=1
            sds = 0.9 * max(sg[t.index(0.2):t.index(5.0)])
            sd1 = sg[t.index(1.0)]
            Label(self, text=str("sms"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sds*1.5,3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            Label(self, text=str("sm1"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sd1*1.5,3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            Label(self, text=str("sds"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sds,3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            Label(self, text=str("sd1"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sd1,3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            Label(self, text=str("pga"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(sg[0],3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            self.button3 = Button(self, text="Write File", bg='green', height=2, width=20,command= lambda:self.mywritefileEstSV(t, sg, tmce, smceg, sds, sd1, plt, sitecl)).grid(row=rr,column=0)
        elif  str(self.entry_SWVel.get()) != "":
            sexp = np.array(su)*siteclBMultp + np.array(sl)*(1-siteclBMultp)
            sexpmce = np.array(smceu)*siteclBMultp + np.array(smcel)*(1-siteclBMultp)
            for label in self.grid_slaves():
                if int(label.grid_info()["row"]) > 22:
                    label.grid_forget()
            ax.plot(t, s, label="Multiperiod Design Spectrum for " + sitecl, color='Red', linewidth=1.0)
            ax.plot(t2, s2, label="2-Period Design Spectrum for " + sitecl, color='Green', linewidth=1.0)
            #ax.plot(tl, sl, label="Lower Bound Design Spectrum for" + sitecll, color='black', linewidth=0.1)
            ax.plot(tl, sexp, label="Interpolated Spectrum for " + str(round(shearwavevel,0)) + " ft/s", color='black', linestyle='--', linewidth=1.0)
            ax.set_xlim([0, 5])
            ax.legend()
            ax.grid()
            ax2.plot(tmce, smce, label="MCE Multiperiod Spectrum", color='Blue', linewidth=1.0)
            ax2.plot(tmce2, smce2, label="MCE 2-Period  Spectrum", color='Green', linewidth=1.0)
            ax2.plot(tmcel, sexpmce, label="Interpolated mCE Spectrum for " + str(round(shearwavevel,0)) + " ft/s", color='black', linestyle='--', linewidth=1.0)
            ax2.set_xlim([0, 5])
            ax2.legend()
            ax2.grid()
            p = rdata["response"]["data"]; rr+=1
            self.title_label = Label(text="ASCE7-22 Seismic Parameter Output").grid(row=rr,column=0, columnspan = 2); rr+=1
            index = 0
            Label(self, text=str("pga"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(s[0],3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            for key, value in p.items():
                if index <= 11:
                    Label(self, text=str(key), relief = "sunken", width= 20).grid(column=0, row=rr)
                    Label(self, text=str(value), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
                index += 1
            self.button3 = Button(self, text="Write File", bg='green', height=2, width=20,command= lambda:self.mywritefileest(rdata, plt, sitecl, sexp)).grid(row=rr,column=0)
        else:
            for label in self.grid_slaves():
                if int(label.grid_info()["row"]) > 22:
                    label.grid_forget()
            ax.plot(t, s, label="Multiperiod Design Spectrum for" + sitecl, color='Red', linewidth=1.0)
            ax.plot(t2, s2, label="2-Period Design Spectrum for" + sitecl, color='Green', linewidth=1.0)
            ax.set_xlim([0, 5])
            ax.legend()
            ax.grid()
            ax2.plot(tmce, smce, label="MCE Multiperiod Spectrum", color='Blue', linewidth=1.0)
            ax2.plot(tmce2, smce2, label="MCE 2-Period  Spectrum", color='Green', linewidth=1.0)
            ax2.set_xlim([0, 5])
            ax2.legend()
            ax2.grid()
            p = rdata["response"]["data"]; rr+=1
            self.title_label = Label(text="ASCE7-22 Seismic Parameter Output").grid(row=rr,column=0, columnspan = 2); rr+=1
            index = 0
            Label(self, text=str("pga"), relief = "sunken", width= 20).grid(column=0, row=rr)
            Label(self, text=str(round(s[0],3)), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
            for key, value in p.items():
                if index <= 11:
                    Label(self, text=str(key), relief = "sunken", width= 20).grid(column=0, row=rr)
                    Label(self, text=str(value), relief = "sunken", width = 20).grid(column=1, row=rr); rr+=1
                index += 1
            self.button3 = Button(self, text="Write File", bg='green', height=2, width=20,command= lambda:self.mywritefile(rdata, plt, sitecl)).grid(row=rr,column=0)            
  


        self.button2 = Button(self, text="Quit", bg='red', height=2, width=20, command=lambda:self.onclick2(plt)).grid(row=rr,column=1)
        

        if self.OpenMap.get()==1:
 #           map = folium.Map(location=[float(lat),float(longt)],zoom_start=12)
 #           folium.Marker([float(lat),float(longt)], popup="Location").add_to(map)
 #           map.save("mymap.html")
 #           webbrowser.open("mymap.html")
            webbrowser.open('http://www.google.com/maps/place/'+ lat +','+longt+'/@'+ lat +','+longt+',12z', new=2)
        if self.locVariation.get()==1:
            self.contourf(lat, longt, riskct, sitecl)
        plt.show()

    def contourf(self, lat, longt, riskct,sitecl):
        messagebox.showinfo("ASCE7-22 Local Variation","Computed for selected site class only,\n Will take some time depending on latency of USGS website\n Select Ok to start")
        self.after(50, self.update)
        nlong = 7
        nlat= 7
        gridspacing = 0.5/60.0
        lat = float(lat)
        longt = float(longt)
        latgrid = np.arange(lat+(nlat//2)*gridspacing, lat-((nlat//2)+0.9)*gridspacing, -gridspacing)
        longgrid = np.arange(longt-(nlong//2)*gridspacing, longt+((nlong//2)+0.9)*gridspacing, gridspacing)
        xLong,xLat = np.meshgrid(longgrid,latgrid)
        ZSDS=np.zeros((nlong,nlat)); ZSD1=np.zeros((nlong,nlat))
        #mapLayer = folium.Map(location=[lat,longt],min_lat=lat-((nlat//2))*gridspacing, max_lat=lat+(nlat//2)*gridspacing, min_lon=longt-(nlong//2)*gridspacing, max_lon=longt+((nlong//2))*gridspacing)
        #mapLayer.save("map.jpg")

        for i in range(nlong):
            for j in range(nlat):
                url = 'https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?latitude='+ str(xLat[i,j]) + '&longitude=' + str(xLong[i,j]) +'&riskCategory='+ riskct +'&siteClass=' + sitecl + '&title=Example'
                try:
                    response = ur.urlopen(url)
   
                except ur.URLError as e:
                    if hasattr(e, 'reason'):
                        print('We failed to reach a server.')
                        print('Reason: ', e.reason)
                        return()
                    elif hasattr(e, 'code'):
                        print('The server couldn\'t fulfill the request.')
                        print('Error code: ', e.code)
                        return() 
                rdata = js.loads(response.read())
                ZSDS[i,j] = rdata["response"]["data"]["sds"]
                ZSD1[i,j] = rdata["response"]["data"]["sd1"]

        #print(ZSDS, ZSD1)
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(121)
        CS = ax.contour(xLong,xLat,ZSDS) 
        ax.set_title('Local Variation of SDS around site')
        ax.text(longt,lat , '. Site '+ str(ZSDS[nlong//2, nlat//2]), fontsize = 10)
        ax.clabel(CS, inline=True, fontsize=10)
        ax = fig.add_subplot(122)
        CS2 = ax.contour(xLong,xLat,ZSD1) 
        ax.set_title('Variation of SD1 around site')
        ax.text(longt, lat, '. Site '+ str(ZSD1[nlong//2, nlat//2]), fontsize = 10)
        ax.clabel(CS2, inline=True, fontsize=10)

        plt.show()

    def quit(self):
        self.progress.stop()
        self.destroy()
        
    def onclick2(self, plt):
        self.progress.stop()
        plt.close('all')
        self.destroy()

    def mywritefileEstSV(self, t, sg, tmce, smceg, sds, sd1, plt, sitecl):
        sitetitle = str(self.entry_Title.get())
        riskct = str(self.SelectedRiskCategory.get())
        address = str(self.entry_Address.get())
        lat = str(self.entry_Latitude.get())
        longt= str(self.entry_Longitude.get())
        with open('ASCE722.txt', 'w') as f:
            f.write("Data source is USGS (ASCE 722 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy.\n")
            f.write("Use of the output of this program does not imply approval by the governing building code bodies responsible for building code approval and interpretation for the building site described by latitude/longitude location.\n")
            f.write("Written by HXB\n \n \n")
            f.write(sitetitle + "\n" + address + "\n")
            f.write("The location is " + lat + ", " + longt +  " and Risk Category "+ riskct + "\n")
            if (self.estSWVel.get()==1 and str(self.entry_SWVel.get()) != ""):
                f.write("Site Class based on an estimated shear wave velocity of " + str(self.entry_SWVel.get()) + "ft/s\n")
                f.write("Lower bound and upper bound site class considered in computation per ASCE 7-22 Section 20.3 and 21.4" + "\n")
            else:
                f.write("Default Site Class based on max of Site Class C, CD, D\n")
            f.write("sms from governing design spectra = " + str(round(sds*1.5, 3)) + "\n")
            f.write("sm1 from governing design spectra = " + str(round(sd1*1.5, 3)) + "\n")
            f.write("sds from governing design spectra = " + str(round(sds, 3)) + "\n")
            f.write("sd1 from governing design spectra = " + str(round(sd1, 3)) + "\n")
            f.write("pga from governing design spectra = " + str(round(sg[0], 3)) + "\n")
            f.write("Governing MultiPeriodDesignSpectrum\n")
            index = len(t)
            j = 0
            while j < index:
                f.write(str(t[j])+ ", " + str(sg[j])+"\n")
                j+= 1
            f.write("Governing MultiPeriodMCErSpectrum\n")
            index = len(tmce)
            j = 0
            while j < index:
                f.write(str(tmce[j])+ ", " + str(smceg[j])+"\n")
                j+= 1
        plt.savefig('spectra.png')
        messagebox.showinfo("Completed", "Wrote file ASCE722.txt and spectra.png")



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
            f.write("Data source is USGS (ASCE 722 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy.\n")
            f.write("Use of the output of this program does not imply approval by the governing building code bodies responsible for building code approval and interpretation for the building site described by latitude/longitude location.\n")
            f.write("Written by HXB\n \n \n")
            f.write(sitetitle + "\n" + address + "\n")
            f.write("The location is " + lat + ", " + longt + " with Site Class " + sitecl + " and Risk Category "+ riskct + "\n")
            if str(self.entry_SWVel.get()) != "":
                f.write("Site Class based on a shear wave velocity of " + str(self.entry_SWVel.get()) + "ft/s\n")
            f.write("pga from design spectra = " + str(round(s[0], 3)) + "\n")
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
        messagebox.showinfo("Completed", "Wrote file ASCE722.txt and spectra.png")


    def mywritefileest(self, ldata, plt, sitecl, sexp):
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
            f.write("Data source is USGS (ASCE 722 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy.\n")
            f.write("Use of the output of this program does not imply approval by the governing building code bodies responsible for building code approval and interpretation for the building site described by latitude/longitude location.\n")
            f.write("Written by HXB\n \n \n")
            f.write(sitetitle + "\n" + address + "\n")
            f.write("The location is " + lat + ", " + longt + " with Site Class " + sitecl + " and Risk Category "+ riskct + "\n")
            if str(self.entry_SWVel.get()) != "":
                f.write("Site Class based on a shear wave velocity of " + str(self.entry_SWVel.get()) + "ft/s\n")
            f.write("pga from design spectra = " + str(round(s[0], 3)) + "\n")
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

            f.write("Interpolated MultiPeriodDesignSpectrum\n")
            index = len(t)
            j = 0
            while j < index:
                f.write(str(t[j])+ ", " + str(sexp[j])+"\n")
                j+= 1
            f.write("MultiPeriodMCErSpectrum\n")
            index = len(tmce)
            j = 0
            while j < index:
                f.write(str(tmce[j])+ ", " + str(smce[j])+"\n")
                j+= 1
        plt.savefig('spectra.png')
        messagebox.showinfo("Completed", "Wrote file ASCE722.txt and spectra.png")

    def about(self):
        messagebox.showinfo('ASCE722', 'Get the Multi-period response spectrum for a site for use with ASCE 7-22.\n\nFree to use.\n\
Data source is USGS (NEHRP 2020 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy. \
Use of the output of this program does not imply approval by the governing building code bodies responsible for building code \
approval and interpretation for the building site described by latitude/longitude location.\n \n\
Written by HXB')

rr=0
root = Root()
root.mainloop()


