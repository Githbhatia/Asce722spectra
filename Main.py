
import numpy as np
import certifi
import ssl
import geopy.geocoders
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import urllib.request as ur
import json as js
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

@st.cache_resource
def myurlopen(url): 
    ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        response = ur.urlopen(url)
    except ur.URLError as e:
        if hasattr(e, 'reason'):
            st.write('We failed to reach a server.')
            st.write('Reason: ', e.reason)
            return()
        elif hasattr(e, 'code'):
            st.write('The server couldn\'t fulfill the request.')
            st.write('Error code: ', e.code)
            return() 
    
    return(response.read())

@st.cache_resource
def mygeolocatorreverse(lat, longt):
    ctx = ssl.create_default_context(cafile=certifi.where())
    #ctx = ssl._create_unverified_context()
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent="STASCE722Spectra", scheme='https')
    try:
        location = geolocator.reverse(str(lat) + " ," + str(longt))
        if location != None:
            address = str(location.address)
            st.write("Using "+ address)
            return(location.address)
        else:
            st.write("Address not found: Continuing using "+ str(lat) + ", " + str(longt)) 
            return("")  
    except GeocoderTimedOut as e:
        st.write("Error: geocode failed on input %s with message %s"%(address, e.message))
        st.write("Continuing using "+ str(lat) + ", " + str(longt))
        return("")

@st.cache_resource
def mygeolocator(address):
    ctx = ssl.create_default_context(cafile=certifi.where())
    #ctx = ssl._create_unverified_context()
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent="STASCE722Spectra", scheme='https')
    try:
        location = geolocator.geocode(address)
        if (location != None):
            lat = str(location.latitude)
            longt = str(location.longitude)
            address = str(location.address)
            st.write("Using "+ str(lat) + ", " + str(longt))
            return(location.latitude, location.longitude, location.address)
        else:
            st.write("Invalid Address:" + "Revise address and try again")
            return(0.0, 0.0, "")
    except GeocoderTimedOut as e:
        st.write("Error: geocode failed on input %s with message %s"%(address, e.message))
        return(0.0, 0.0, "")


    

def onclick():

    global address, lat,longt, textout, riskct, sitecl,sds
   
    if swv != 0.0:
        try:
            shearwavevel = float(swv)
        except ValueError:
            st.write("Invalid Shear Wave Velocity:"+ "Enter shear wave velocity in ft/sec and try again")
            return
        if shearwavevel==0:
            st.write("Invalid Shear Wave Velocity:"+ "Enter a non-zero shear wave velocity in ft/sec and try again")
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
                
        if estimatedswv==1:
            for a, b in shearwavevellimits:
                if shearwavevel/1.3 <= b:
                    sitecll = a
                    break
            for a, b in shearwavevellimits:
                if shearwavevel*1.3 <= b:
                    siteclu = a
                    break

        placeholder.selectbox("Site Class",siteClassList,index = siteClassList.index(sitecl)) 
            
        
    elif siteclass=="Default":
        sitecl = "CD"
        siteclu = "C"
        sitecll = "D"
    else:
        sitecl = siteclass
    if sitecl == 'F': 
        st.write("Invalid Shear Wave Velocity:" + "Site Class F, Requires site response analysis studies")
        return(0)
    
    #print(sitecll+" "+siteclu)
    #print(st.session_state.siteclass)

    if siteclass=="Default" and swv == 0.0:
        st.write("Using site class " + siteclass)
    else:
        st.write("Using site class " + sitecl)

    
    ctx = ssl.create_default_context(cafile=certifi.where())
    #ctx = ssl._create_unverified_context()
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent="STASCE722Spectra", scheme='https')
    sitetitle = mysite
    riskct = riskc
    address = addressg



    if address =="":
        lat = latitude
        longt = longitude
        address = mygeolocatorreverse(lat, longt)
    else:
        lat, longt, address = mygeolocator(address)
        if lat == 0.0 and longt == 0.0:
            st.stop()
            

    
    df = pd.DataFrame({"lat":[float(lat)], "lon":[float(longt)]})
    st.map(df)      


    url = 'https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?latitude='+ str(lat) + '&longitude=' + str(longt) +'&riskCategory='+ riskct +'&siteClass=' + sitecl + '&title=Example'
    
    if  swv != 0.0 or siteclass=="Default":
        urll = 'https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?latitude='+ str(lat) + '&longitude=' + str(longt) +'&riskCategory='+ riskct +'&siteClass=' + sitecll + '&title=Example'
        urlu = 'https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?latitude='+ str(lat) + '&longitude=' + str(longt) +'&riskCategory='+ riskct +'&siteClass=' + siteclu + '&title=Example'
        


    response = myurlopen(url)
    if swv != 0.0 or siteclass=="Default":
        responsel = myurlopen(urll)
        responseu = myurlopen(urlu)

    
    rdata = js.loads(response)
    if swv != 0.0 or siteclass=="Default":           
        rdatal = js.loads(responsel)
        rdatau = js.loads(responseu)

    # if self.SaveJson.get() == 1:
    #     with open("ASCE722.json", "w") as write_file:
    #         js.dump(rdata, write_file)
    #     if str(self.entry_SWVel.get()) != "" or str(self.SelectedSiteClass.get())=="Default":
    #         with open("ASCE722_lowerbound.json", "w") as write_file:
    #             js.dump(rdatal, write_file)
    #         with open("ASCE722_upperbound.json", "w") as write_file:
    #             js.dump(rdatau, write_file)

    output = 'Output for Latitude = ' + str(lat) + ' Longitude = ' + str(longt)
    t = rdata["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
    s = rdata["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]

    t2 = rdata["response"]["data"]["twoPeriodDesignSpectrum"]["periods"]
    s2 = rdata["response"]["data"]["twoPeriodDesignSpectrum"]["ordinates"]
        
    tmce = rdata["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
    smce = rdata["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]



    tmce2 = rdata["response"]["data"]["twoPeriodMCErSpectrum"]["periods"]
    smce2 = rdata["response"]["data"]["twoPeriodMCErSpectrum"]["ordinates"]

    if swv != 0.0 or siteclass=="Default":    
        tl = rdatal["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
        sl = rdatal["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]
        
        tu = rdatau["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
        su = rdatau["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]

        tmcel = rdatal["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
        smcel = rdatal["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]

        tmceu = rdatau["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
        smceu = rdatau["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]

    fig = plt.figure(figsize=(10, 10))
    ax = fig.subplots(2,1)
    ax[0].set_xlabel('Period')
    ax[0].set_title(sitetitle + " Design Spectrum")

    ax[1].set_xlabel('Period')
    ax[1].set_title(sitetitle + " MCE Spectrum")

    if (estimatedswv and swv != 0.0):

        sg = [max(sl,s,su) for sl,s,su in zip(sl,s,su)]
        ax[0].plot(t, sl, label="Multiperiod Des Spec lower bound SC= "+ sitecll, color='Red', linewidth=1.0)
        ax[0].plot(t, s, label="Multiperiod Des Spec SC= " + sitecl, color='Blue', linewidth=1.0)
        ax[0].plot(t, su, label="Multiperiod Des Spec upper bound SC= "+ siteclu, color='Green', linewidth=1.0)
        ax[0].plot(t, sg, label="Govering Multiperiod Des Spec", color='Black', linestyle='--', linewidth=2.0)
        ax[0].set_xlim([0, 5])
        ax[0].legend()  
        ax[0].grid()
        smcel = rdatal["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
        smceu = rdatau["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
        smceg = [max(smcel,smce,smceu) for smcel,smce,smceu in zip(smcel,smce,smceu)]
        ax[1].plot(tmce, smcel, label="MCE Multiperiod lower bound SC= "+ sitecll, color='Red', linewidth=1.0)
        ax[1].plot(tmce, smce, label="MCE Multiperiod Spec SC= " + sitecl, color='Blue', linewidth=1.0)
        ax[1].plot(tmce, smceu, label="MCE Multiperiod upper bound SC= "+ siteclu, color='Green', linewidth=1.0)
        ax[1].plot(tmce, smceg, label="Govering MCE Multiperiod", color='Black', linestyle='--', linewidth=2.0)
        ax[1].set_xlim([0, 5])
        ax[1].legend() 
        ax[1].grid()
        

        
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

        st.subheader("ASCE7-22 Seismic Parameter Output")
        st.write("Based on est. shear wave velocity per ASCE 7-22 Section 20.3 and 21.4")
        df = pd.DataFrame(
        {'Parameter':["sms","sm1","sds","sd1","pga"],'Values':[str(round(sds*1.5,3)),str(round(sd1*1.5,3)),str(round(sds,3)),str(round(sd1,3)),str(round(sg[0],3))]}
        )
        df.set_index('Parameter', inplace=True)
        st.dataframe(df)

        dfs=pd.DataFrame({"time period":t,"Governing Multiperiod Spec": sg, "Governing MCE Multiperiod":smceg })
        st.dataframe(dfs)
        textout = mywritefileEstSV(t, sg, tmce, smceg, sds, sd1, sitecl)

    elif  swv != 0.0:
        sexp = np.array(su)*siteclBMultp + np.array(sl)*(1-siteclBMultp)
        sexpmce = np.array(smceu)*siteclBMultp + np.array(smcel)*(1-siteclBMultp)
        ax[0].plot(t, s, label="Multiperiod Design Spectrum for " + sitecl, color='Red', linewidth=1.0)
        ax[0].plot(t2, s2, label="2-Period Design Spectrum for " + sitecl, color='Green', linewidth=1.0)
        #ax[0].plot(tl, sl, label="Lower Bound Design Spectrum for" + sitecll, color='black', linewidth=0.1)
        ax[0].plot(tl, sexp, label="Interpolated Spectrum for " + str(round(shearwavevel,0)) + " ft/s", color='black', linestyle='--', linewidth=1.0)
        ax[0].set_xlim([0, 5])
        ax[0].legend()
        ax[0].grid()
        ax[1].plot(tmce, smce, label="MCE Multiperiod Spectrum", color='Blue', linewidth=1.0)
        ax[1].plot(tmce2, smce2, label="MCE 2-Period  Spectrum", color='Green', linewidth=1.0)
        ax[1].plot(tmcel, sexpmce, label="Interpolated mCE Spectrum for " + str(round(shearwavevel,0)) + " ft/s", color='black', linestyle='--', linewidth=1.0)
        ax[1].set_xlim([0, 5])
        ax[1].legend()
        ax[1].grid()
        p = rdata["response"]["data"].items()
        st.subheader("ASCE7-22 Seismic Parameter Output")
        df = pd.DataFrame(p)
        df = df[0:11]
        df.columns = ['Parameter','Values']
        df['Values'] = df['Values'].astype(str)
        df.set_index('Parameter', inplace=True)
        st.dataframe(df)
        dfs=pd.DataFrame({"time period":t,"Multiperiod Spec": s, "Interpolated Spec": sexp  ,"MCE Multiperiod":smce, "Interpolated MCE spec": sexpmce })
        st.dataframe(dfs)
        sds =float(df.loc["sds"].values[0])
        textout = mywritefileest(rdata, sitecl, sexp)

    elif siteclass=="Default":   

        sg = [max(sl,s,su) for sl,s,su in zip(sl,s,su)]
        ax[0].plot(t, sl, label="Multiperiod Des Spec lower bound SC= "+ sitecll, color='Red', linewidth=1.0)
        ax[0].plot(t, s, label="Multiperiod Des Spec SC= " + sitecl, color='Blue', linewidth=1.0)
        ax[0].plot(t, su, label="Multiperiod Des Spec upper bound SC= "+ siteclu, color='Green', linewidth=1.0)
        ax[0].plot(t, sg, label="Govering Multiperiod Des Spec", color='Black', linestyle='--', linewidth=2.0)
        ax[0].set_xlim([0, 5])
        ax[0].legend()  
        ax[0].grid()
        smcel = rdatal["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
        smceu = rdatau["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
        smceg = [max(smcel,smce,smceu) for smcel,smce,smceu in zip(smcel,smce,smceu)]
        ax[1].plot(tmce, smcel, label="MCE Multiperiod lower bound SC= "+ sitecll, color='Red', linewidth=1.0)
        ax[1].plot(tmce, smce, label="MCE Multiperiod Spec SC= " + sitecl, color='Blue', linewidth=1.0)
        ax[1].plot(tmce, smceu, label="MCE Multiperiod upper bound SC= "+ siteclu, color='Green', linewidth=1.0)
        ax[1].plot(tmce, smceg, label="Govering MCE Multiperiod", color='Black', linestyle='--', linewidth=2.0)
        ax[1].set_xlim([0, 5])
        ax[1].legend() 
        ax[1].grid()
 

        sds = 0.9 * max(sg[t.index(0.2):t.index(5.0)])
        sd1 = sg[t.index(1.0)]
        st.subheader("ASCE7-22 Seismic Parameter Output")
        st.write("Default = Max of Site Class C, CD, D")
        df = pd.DataFrame(
        {'Parameter':["sms","sm1","sds","sd1","pga"],'Values':[str(round(sds*1.5,3)),str(round(sd1*1.5,3)),str(round(sds,3)),str(round(sd1,3)),str(round(sg[0],3))]}
        )
        df.set_index('Parameter', inplace=True)
        st.dataframe(df)
        sds =float(df.loc["sds"].values[0])
        dfs=pd.DataFrame({"time period":t,"Governing Multiperiod Spec": sg, "Governing MCE Multiperiod":smceg })
        st.dataframe(dfs)
        textout = mywritefileEstSV(t, sg, tmce, smceg, sds, sd1, sitecl)
    else:
        ax[0].plot(t, s, label="Multiperiod Design Spectrum for " + sitecl, color='Red', linewidth=1.0)
        ax[0].plot(t2, s2, label="2-Period Design Spectrum for " + sitecl, color='Green', linewidth=1.0)
        ax[0].set_xlim([0, 5])
        ax[0].legend()
        ax[0].grid()
        ax[1].plot(tmce, smce, label="MCE Multiperiod Spectrum", color='Blue', linewidth=1.0)
        ax[1].plot(tmce2, smce2, label="MCE 2-Period  Spectrum", color='Green', linewidth=1.0)
        ax[1].set_xlim([0, 5])
        ax[1].legend()
        ax[1].grid()
        p = rdata["response"]["data"].items()
        st.subheader("ASCE7-22 Seismic Parameter Output")
        df = pd.DataFrame(p)
        df = df[0:11]
        df.columns = ['Parameter','Values']
        df['Values'] = df['Values'].astype(str)
        df.set_index('Parameter', inplace=True)
        st.dataframe(df)
        sds =float(df.loc["sds"].values[0])
        dfs=pd.DataFrame({"time period":t,"Multiperiod Spec": s, "MCE Multiperiod":smce })
        st.dataframe(dfs)
        textout = mywritefile(rdata, sitecl)

    st.pyplot(fig)

    return()

def contourf(lat, longt, riskct):
    sitecl = siteclass
    nlong = 7
    nlat= 7
    gridspacing = 0.5/60.0
    lat = float(lat)
    longt = float(longt)
    latgrid = np.arange(lat+(nlat//2)*gridspacing, lat-((nlat//2)+0.9)*gridspacing, -gridspacing)
    longgrid = np.arange(longt-(nlong//2)*gridspacing, longt+((nlong//2)+0.9)*gridspacing, gridspacing)
    xLong,xLat = np.meshgrid(longgrid,latgrid)
    ZSDS=np.zeros((nlong,nlat)); ZSD1=np.zeros((nlong,nlat))
    st.write("Grid Used:")
    df = pd.DataFrame({"lat":xLat.flatten(), "lon":xLong.flatten()})
    st.map(df)  
    mesg = st.empty()

    for i in range(nlong):
        for j in range(nlat):
            mesg.write("Getting gird " + str(i) + ", " + str(j))
            url = 'https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?latitude='+ str(xLat[i,j]) + '&longitude=' + str(xLong[i,j]) +'&riskCategory='+ riskct +'&siteClass=' + sitecl + '&title=Example'
            response = myurlopen(url)
            rdata = js.loads(response)
            ZSDS[i,j] = rdata["response"]["data"]["sds"]
            ZSD1[i,j] = rdata["response"]["data"]["sd1"]
    mesg.write("Completed")
    #print(ZSDS, ZSD1)
    fig = plt.figure(figsize=(10, 20))
    ax = fig.add_subplot(211)
    CS = ax.contour(xLong,xLat,ZSDS) 
    ax.set_title('Local Variation of SDS around site')
    ax.text(longt,lat , '. Site '+ str(ZSDS[nlong//2, nlat//2]), fontsize = 10)
    ax.clabel(CS, inline=True, fontsize=10)
    ax = fig.add_subplot(212)
    CS2 = ax.contour(xLong,xLat,ZSD1) 
    ax.set_title('Variation of SD1 around site')
    ax.text(longt, lat, '. Site '+ str(ZSD1[nlong//2, nlat//2]), fontsize = 10)
    ax.clabel(CS2, inline=True, fontsize=10)

    st.pyplot(fig)



def mywritefileEstSV(t, sg, tmce, smceg, sds, sd1, sitecl):
    sitetitle = mysite
    riskct = riskc

    textout = ""

    textout += "Data source is USGS (ASCE 722 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy.\n"
    textout += "Use of the output of this program does not imply approval by the governing building code bodies responsible for building code approval and interpretation for the building site described by latitude/longitude location.\n"
    textout += "\n \n"
    textout += sitetitle + "\n" + address + "\n"
    textout += "The location is " + str(lat) + ", " + str(longt) +  " and Risk Category "+ riskct + "\n"
    if (estimatedswv and swv == 0.0):
        textout += "Site Class based on an estimated shear wave velocity of " + str(swv) + "ft/s\n"
        textout += "Lower bound and upper bound site class considered in computation per ASCE 7-22 Section 20.3 and 21.4" + "\n"
    else:
        textout += "Default Site Class based on max of Site Class C, CD, D\n"
    textout += "sms from governing design spectra = " + str(round(sds*1.5, 3)) + "\n"
    textout += "sm1 from governing design spectra = " + str(round(sd1*1.5, 3)) + "\n"
    textout += "sds from governing design spectra = " + str(round(sds, 3)) + "\n"
    textout += "sd1 from governing design spectra = " + str(round(sd1, 3)) + "\n"
    textout += "pga from governing design spectra = " + str(round(sg[0], 3)) + "\n"
    textout += "Governing MultiPeriodDesignSpectrum\n"
    index = len(t)
    j = 0
    while j < index:
        textout += str(t[j])+ ", " + str(sg[j])+"\n"
        j+= 1
    textout += "Governing MultiPeriodMCErSpectrum\n"
    index = len(tmce)
    j = 0
    while j < index:
        textout += str(tmce[j])+ ", " + str(smceg[j])+"\n"
        j+= 1
    return(textout)




def mywritefile( ldata, sitecl):
    sitetitle = mysite
    riskct = riskc

    textout = ""
    index = 0
    p = ldata["response"]["data"]
    t = ldata["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
    s = ldata["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]
    tmce = ldata["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
    smce = ldata["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
    textout += "Data source is USGS (ASCE 722 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy.\n"
    textout += "Use of the output of this program does not imply approval by the governing building code bodies responsible for building code approval and interpretation for the building site described by latitude/longitude location.\n"
    textout += "\n \n"
    textout += sitetitle + "\n" + address + "\n"
    textout += "The location is " + str(lat) + ", " + str(longt) + " with Site Class " + sitecl + " and Risk Category "+ riskct + "\n"
    if swv != 0.0:
        textout += "Site Class based on a shear wave velocity of " + str(swv) + "ft/s\n"
    textout += "pga from design spectra = " + str(round(s[0], 3)) + "\n"
    for key, value in p.items():
        if index <= 11:
            textout += str(key)+ ", " + str(value)+"\n"  
        index += 1
    
    textout += "MultiPeriodDesignSpectrum\n"
    index = len(t)
    j = 0
    while j < index:
        textout += str(t[j])+ ", " + str(s[j])+"\n"
        j+= 1
    textout += "MultiPeriodMCErSpectrum\n"
    index = len(tmce)
    j = 0
    while j < index:
        textout += str(tmce[j])+ ", " + str(smce[j])+"\n"
        j+= 1
    return(textout)


def mywritefileest(ldata, sitecl, sexp):
    sitetitle = mysite
    riskct = riskc

    textout = ""
    index = 0
    p = ldata["response"]["data"]
    t = ldata["response"]["data"]["multiPeriodDesignSpectrum"]["periods"]
    s = ldata["response"]["data"]["multiPeriodDesignSpectrum"]["ordinates"]
    tmce = ldata["response"]["data"]["multiPeriodMCErSpectrum"]["periods"]
    smce = ldata["response"]["data"]["multiPeriodMCErSpectrum"]["ordinates"]
    textout += "Data source is USGS (ASCE 722 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy.\n"
    textout += "Use of the output of this program does not imply approval by the governing building code bodies responsible for building code approval and interpretation for the building site described by latitude/longitude location.\n"
    textout += "\n \n"
    textout += sitetitle + "\n" + address + "\n"
    textout += "The location is " + str(lat) + ", " + str(longt) + " with Site Class " + sitecl + " and Risk Category "+ riskct + "\n"
    if swv != 0.0 :
        textout += "Site Class based on a shear wave velocity of " + str(swv) + "ft/s\n"
    textout += "pga from design spectra = " + str(round(s[0], 3)) + "\n"
    for key, value in p.items():
        if index <= 11:
            textout += str(key)+ ", " + str(value)+"\n"     
        index += 1
    
    textout += "MultiPeriodDesignSpectrum\n"
    index = len(t)
    j = 0
    while j < index:
        textout += str(t[j])+ ", " + str(s[j])+"\n"
        j+= 1

    textout += "Interpolated MultiPeriodDesignSpectrum\n"
    index = len(t)
    j = 0
    while j < index:
        textout += str(t[j])+ ", " + str(sexp[j])+"\n"
        j+= 1
    textout += "MultiPeriodMCErSpectrum\n"
    index = len(tmce)
    j = 0
    while j < index:
        textout += str(tmce[j])+ ", " + str(smce[j])+"\n"
        j+= 1
    return(textout)



st.subheader(":blue[ASCE7-22 Seismic Parameter Input]")
sds = 0.0

# st.query_params.from_dict({"address": "elk grove, CA", "title": "Cool location", "long": -120, "lat": 39, "shearwavevelo": 1200})

if "title" in st.query_params:
    inTitle = st.query_params["title"]
else:
    inTitle = "My Title"

if "address" in st.query_params:
    inAdd = st.query_params["address"]
else:
    inAdd = ""

if "long" in st.query_params:
    inLong = float(st.query_params["long"])
else:
    inLong = -121.0

if "lat" in st.query_params:
    inLat = float(st.query_params["lat"])
else:
    inLat = 38.0

RiskCategoryList=["I","II","III","IV"]
if "riskcat" in st.query_params:
    if st.query_params["riskcat"] in RiskCategoryList:
        inRisk = st.query_params["riskcat"]
    else:
        inRisk = "IV"
else:
    inRisk = "IV"

if "shearwavevelo" in st.query_params:
    inSwv = float(st.query_params["shearwavevelo"])
else:
    inSwv = 0.0

st.write("Data source is USGS (ASCE 722 Database) and OpenStreetMaps.\nAuthors do not assume any responsibility or liability for its accuracy.")
st.write("Use of the output of this program does not imply approval by the governing building code bodies responsible for building code approval and interpretation for the building site described by latitude/longitude location.")
st.divider()
mysite = st.text_input("Title for report",inTitle)
st.write("Either enter Shear Wave Velocity or pick Site Class" )
st.write("(Shear Wave Velocity will be used when entered)")


c1, c2 =st.columns(2)
with c1:
    t1, t2 = st.tabs(["Shear Wave Velocity", "Site Class"])
    with t1:
        swv = st.number_input("Shear Wave Velocity (ft/s)",value = inSwv, step = 100.0, min_value = 0.0, key="swv")
        estimatedswv= st.checkbox("Estimated Shear Wave Velocity?")

    with t2:
        placeholder = st.empty()
        siteClassList=["A","B","BC","C","CD","D","DE","E", "Default"]
        siteclass = placeholder.selectbox("Site Class",siteClassList,index = 8, key="siteclass")
        if swv != 0:
            st.write("Note: Clear Shear Wave Velocity to 0.0 to use generate spectra via site class")
with c2:

    riskc = st.selectbox("Risk Category",RiskCategoryList, index = RiskCategoryList.index(inRisk))

st.divider()
st.write("Either provide Address or Lat/Long Pair (leave Address blank)")

tab1, tab2 = st.tabs(["Address", "Lat/Long"])

with tab1:
    addressg = st.text_input("Address", inAdd, placeholder="123, streat name, city, CA")

with tab2:
    latitude= st.number_input("Latitude",value=inLat, step = 0.1, min_value = -90.0, max_value= 90.0)
    longitude= st.number_input("Longitude",value =inLong, step = 0.1, min_value =-180.0, max_value=180.0)
    if addressg != "":
        st.write("Note: Clear address to use generate spectra using lat/long pair")

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.button('Run', on_click=click_button)

# st.write(st.session_state)
if st.session_state.clicked:
    onclick()
    st.subheader("Download output file for Spectra")
    sfile= st.checkbox("Save output file")
    if sfile:
        st.download_button("Save output file", textout, file_name="respspectra.txt",)

sds_latex = "S_{DS}"
sd1_latex = "S_{D1}"
if st.session_state.clicked:
    st.subheader("ASCE7-22 Local Variation of Seismic Parameters")
    st.write("Computed for selected site class only,\n Will take some time depending on latency of USGS website,\n Select to start")
    locvart= st.checkbox(f"Check Local Variation of ${sds_latex}$ and ${sd1_latex}$")
    if locvart==1:
        contourf(lat, longt, riskct)

st.divider()


if st.session_state.clicked:
    st.subheader(":blue[ASCE7-22 Fp Calculation]")
    locvart= st.checkbox("Compute Fp")
    FP="F_{p}"
    if locvart==1:
        st.write("USING THE DEFAULT OPTIONS WILL LEAD TO CONSERVATIVE RESULTS")
        sds = st.number_input(f"${sds_latex}$, as obtained above, can modify here", value= sds, format="%0.3f")
        df = pd.read_csv('ASCE722Ch13.csv')
        df.set_index('Menuitems', inplace=True)
        selecteditem = st.selectbox("Select Nonstructural item (ASCE 7-22 Tables 13.5-1 and 13.6-1)",df.index, index = 1, key="nonstructural")
        car0 = df.loc[selecteditem].values[0]
        car1 = df.loc[selecteditem].values[1]
        rPO = df.loc[selecteditem].values[2]
        omegaOP = df.loc[selecteditem].values[3]

        sc1,sc2 =st.columns(2)
        with sc1:
            I_p = "I_{p}"
            iP = float(st.selectbox(f"${I_p}$, Component Importance Factor",(1.0,1.5), index = 1))

        sc3,sc4 =st.columns(2)
        with sc3:
            Z = "Z"
            # z = st.number_input(f"${Z}$, height above base",value= 90.0)
            zStr = st.text_input(f"${Z}$, height above base (multiple ok,separate with commas)",str("0, 15, 30, 45, 60, 75, 90, 100"))

        zLbl = st.text_input("Labels corresponding to Z values (Separate with commas,Optional)",str("Grnd Level, Level 2, Level 3, Level 4, Level 5, Level 6, Mech Level, Roof"))
        zLblist = [i.strip() for i in zLbl.split(",")]
        try:
            z =[float(i) for i in zStr.split(",")]
        except ValueError:
            st.write("Invalid input, Please enter numbers separated by commas")
            st.stop()

        if len(z) > len(zLblist):
            for i in range(len(z)-len(zLblist)):
                zLblist.append("")
        if len(z) < len(zLblist):
            for i in range(len(zLblist)-len(z)):
                zLblist.pop()

        with sc4:
            H = "H"
            h = st.number_input(f"${H}$, Average roof height of structure in ft",value= 100.0)

        st.divider()
        knownstsys = st.toggle("Structural System Selection (Unknown system assumed if not enabled)", key="structuralselect")
        if knownstsys:
            dfs = pd.read_csv('ASCE722StructuralSystems.csv')
            dfs.set_index('StructuralSystem', inplace=True)
            selecteditem = st.selectbox("Select Structural System of the Building (ASCE 7-22 Table 12.2-1):",dfs.index, index = 49, key="structural")
            r = dfs.loc[selecteditem].values[0]
            oM = dfs.loc[selecteditem].values[1]
        I_e = "I_{e}"
        ie = float(st.selectbox(f"${I_e}$, Importance Factor for Building",(1.0,1.25,1.5), index = 2))
        if knownstsys:
            c1,c2 = st.columns(2)
            with c1:
                R= "R"
                st.write(f"${R}$, Response modification Value = "+ str(round(r,2)))
            with c2:
                Om = "\\Omega_{o}"
                st.write(f"${Om}$ = " + str(round(oM,2)))
            rU = max((1.1*(r/(ie*oM)))**0.5, 1.3)
        else:
            rU = 1.3
        
        Ru = "R_{\\mu}"
        st.write(f"${Ru}$ = " +str(round(rU,3)) + " (1.0 used for z = 0.0)")

        st.divider()
        knownperiod = st.toggle("Period Known (if not enabled, period is calculated based on Height H)", key="periodselect")
        if knownperiod:
            Ta = "T_{a}"
            tA = st.number_input(f"${Ta}$, Lowest fundamental period of structure:",value= 0.5)
        else:
            tA = 0.02*h**0.75
            Ta = "T_{a} = C_t H^x = "
            st.write(f"Per ASCE 7-22 Eq 12.8-8 (for \"all other structural systems\"):" )
            st.write(f"${Ta}$" +str(round(tA,3))+ " secs")
        st.divider()




        def getHf(zhratio):
            a1 = min(1/tA,2.5)
            a2 = max((1-(0.4/tA)**2),0.0)
            hF = 1+ a1*zhratio + a2*zhratio**10 
            # print ("Hf = " + str(hF))   
            return(hF)

        zhlist = np.concatenate((np.array([0.0,0.001]),np.arange(0.002, 1.001, 0.001)),axis=0)

        zh = [None]*len(z);hF = [None]*len(z);fP = [None]*len(z)
        fPMax = 1.6*sds*iP
        fPMin = 0.3*sds*iP
        fPMaxstr = "1.6 S_{DS} I_p W_p"
        fPMinstr = "0.3 S_{DS} I_p W_p"
        for i in range(len(z)):
            zh[i] =z[i]/h
            hF[i] = getHf(zh[i])
        # Hf = "H_{f}"
        # st.write(f"${Hf}$ = " +str(round(hF,3)))
            if z[i] == 0.0:
                fP[i] = 0.4*sds*iP*(hF[i]/1.0)*(car0/rPO)
            else:
                fP[i] = 0.4*sds*iP*(hF[i]/rU)*(car1/rPO)

            fP[i] = min(max(fP[i],fPMin),fPMax)


        Wp = "W_{p}"
        st.write(":red[ASCE 7-22 Equation 13.3.1:]")
        st.latex(r'''\color{red} F_{p} = 0.4 S_{DS} I_{p} \left( \frac{H_{f}}{R_{\mu}} \right) \left( \frac{C_{AR}}{R_{po}} \right) W_{p}''')
        c1,c2 = st.columns(2)
        with c1:
            tfPmin=str(round(fPMin,3))
            st.write(f":red[Minimum ${FP}$ = ${fPMinstr}$ = {tfPmin} ${Wp}$]")
        with c2:
            tfmax=str(round(fPMax,3))
            st.write(f":red[Maximum ${FP}$ = ${fPMaxstr}$ = {tfmax} ${Wp}$]")
        c1,c2 = st.columns(2)
        with c1:
            CAR0 = "C_{AR}"
            st.write(f"${CAR0}$ supported at or below grade plane = " + str(car0))
        with c2:
            CAR1 = "C_{AR}"
            st.write(f"${CAR1}$ above grade plane,supported by structure = " + str(car1))   
        Rpo = "R_{PO}"
        st.write(f"${Rpo}$ = " + str(rPO))
        Omop = "\\Omega_{op}"
        st.write(f" ${Omop}$ to be used for concrete or masonry post-installed anchors = " + str(round(omegaOP,3)) )

        fPlist = []
        for i in range(len(zhlist)):
            hFL = getHf(zhlist[i])
            if zhlist[i] == 0.0:
                fPlist.append(min(max(0.4*sds*iP*(hFL/1.0)*(car0/rPO),fPMin),fPMax))
            else:
                fPlist.append(min(max(0.4*sds*iP*(hFL/rU)*(car1/rPO),fPMin),fPMax))
        st.write(f":blue[Governing ${FP}$:]")
        dfsfP=pd.DataFrame({"Location":zLblist,"Z":z,"Z/H": zh,"Hf": hF, "Fp/Wp": fP})
        st.dataframe(dfsfP, hide_index=True)

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)
        ax.plot(fPlist, zhlist, label="Calculated Fp", color='Red', linewidth=1.0)
        for i in range(len(z)):
            ax.plot(fP[i], zh[i], marker='o', label="Governing Fp", color='Black', linestyle='--', linewidth=2.0)
            axmin,axmax = ax.get_xlim()
            arrowlength = (axmax - axmin)/20
            if z[i] >0.85* h:
                ax.annotate(f"{round(fP[i],3)} at " + str(z[i]) + " ("+ zLblist[i] + ")", ha = 'right', xy=(fP[i], zh[i]), xytext=(fP[i]-arrowlength, zh[i]+0.005), arrowprops=dict(facecolor='black', shrink=0.05))
            else:       
                ax.annotate(f"{round(fP[i],3)} at " + str(z[i]) + " ("+ zLblist[i] + ")", xy=(fP[i], zh[i]), xytext=(fP[i]+arrowlength, zh[i]+0.005), arrowprops=dict(facecolor='black', shrink=0.05))
        ax.grid()
        ax.set_xlabel("Fp/Wp")
        ax.set_ylabel("Z/H")
        ax.set_title("Variation of Fp with Z/H")
        st.pyplot(fig)

        


     

        




