# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 23:08:55 2022

@author: Nikolas Ermando
"""
# Import Libraries
import streamlit as st
from bs4 import BeautifulSoup as soup
import requests
import pandas as pd
import numpy as np
import re
import plotly.express as px

# Header streamlit
st.write("""
# World COVID-19 Data Analysis
##### Dibuat oleh Nikolas Ermando
Aplikasi ini bertujuan untuk menganalisis angka dan data-data COVID-19 di dunia. Ataupun tujuan aplikasi ini dapat dirangkai dalam bentuk sebagai berikut:
* Memvisualisasikan angka-angka kasus, sembuh maupun kematian yang disebabkan oleh virus COVID-19 terkini.
* Mencari tahu apakah pola angka COVID-19 bergantung pake lokasi geografis, ekonomi, maupun faktor lain dari suatu negara.
* Menyederhanakan isi dataset lewat penjelasan dan visualisasi yang ditampilkan.
* Memberikan informasi yang dinilai relevan sehingga dapat membantu upaya pengatasan COVID-19 di Dunia.
Dataset dipreroleh dari [Worldometer](https://www.worldometers.info/coronavirus/).
""")
st.write("Libraries yang dipakai : streamlit, pandas, beautifulsoup4, dan plotly")

# Webscrapping dengan Beautiful Soup
def covid_data_scrapping(tableid):
    url = 'https://www.worldometers.info/coronavirus/'
    response = requests.get(url, allow_redirects=True)
    soup_response = soup(response.text, 'html.parser')
    table = soup_response.find("table", id = tableid).find('tbody')
    rows = table.find_all('tr', style = re.compile(r'background-color:#EAF7D5|background-color:#F0F0F0|'''))
    global_info = []
    for row in rows:
        columns = row.find_all('td')
        country_info = [column.text.strip() for column in columns]
        global_info.append(country_info)
    del global_info[:7]
    variables = ['Number','Country','Total Cases', 'New Cases','Total Deaths','New Deaths','Total Recovered', 'New Recovered','Active Cases','Serious Critical','Tot Cases/1M pop','Death/1M pop','Total Tests','Tests/1M pop','Population','Country Region','','','','','',''] 
    dataframe = pd.DataFrame(global_info, columns = variables)
    dataframe.drop(dataframe.iloc[:,[16,17,18,19,20,21]],axis=1,inplace=True)
    return dataframe

# Mengaplikasi fungsi webscrapping ke variable dataframe
df_today = covid_data_scrapping('main_table_countries_today')
df_yesterday = covid_data_scrapping('main_table_countries_yesterday2')

# Menghapus Kolom new cases, new deaths karena data dinilai tidak begitu terlalu update
df_today.drop(['New Cases','New Deaths','New Recovered'], axis = 1, inplace = True)
df_yesterday.drop(['New Cases','New Deaths','New Recovered'], axis = 1, inplace = True)

# Menganti datatype dari object menjadi numeric (int/float)
dftoday = df_today.apply(lambda x : pd.to_numeric(x.astype(str).str.replace(',',''),errors='coerce'))
masktoday = dftoday.isnull().all()
dftoday.loc[:,masktoday] = dftoday.loc[:,masktoday].combine_first(df_today)
dftoday.fillna(0,inplace=True)
dfyesterday = df_yesterday.apply(lambda x : pd.to_numeric(x.astype(str).str.replace(',',''),errors='coerce'))
maskyesterday = dfyesterday.isnull().all()
dfyesterday.loc[:,maskyesterday] = dfyesterday.loc[:,maskyesterday].combine_first(df_yesterday)
dfyesterday.fillna(0,inplace=True)

# Menghapus kolom number dan mengsorting data berdasarkan nama negara
dftoday.drop(['Number'],axis = 1, inplace = True)
dfyesterday.drop(['Number'],axis =1, inplace = True)
dftoday = dftoday.sort_values(by='Country').reset_index(drop=True)
dfyesterday = dfyesterday.sort_values(by='Country').reset_index(drop=True)

# Menambahkan kolom baru pada dataframe today
dftoday['New Cases'] = dftoday['Total Cases'] - dfyesterday['Total Cases']
dftoday['New Deaths'] = dftoday['Total Deaths'] - dfyesterday['Total Deaths']
dftoday['New Recovered'] = dftoday['Total Recovered'] - dfyesterday['Total Recovered']
dftoday = dftoday.sort_values(by='Total Cases',ascending=False).reset_index(drop=True)

#Webscrapping data
st.subheader("1. Webscrapping Data")
st.write("""
    Hal Pertama yang dilakukan adalah melakukan webscrapping pada website [Worldometer](https://www.worldometers.info/coronavirus/) dengan menggunakan library **beautifulsoup4**.
    Webscrapping dilakukan secara tahap bertahap, yakni:
* Dimulai terlebih dahulu dari men-request url.
* Kemudian mengidentifikasi jenis struktur website yang akan di pecah.
* Kemudian mencari tag table dengan id yang mewakili tabel data COVID-19.
* Mencari tag row dan cell untuk memperoleh data pada masing-masing cell dengan style tertentu.
* Menyusun text yang telah diperoleh lewat webscrapping kedalam wadah yang berbentuk dataframe.
Dilampirkan code webscrapping pada markdown dibawah ini:""")
    
webscrappingcode = '''
def covid_data_scrapping(tableid):
    url = 'https://www.worldometers.info/coronavirus/'
    response = requests.get(url, allow_redirects=True)
    soup_response = soup(response.text, 'html.parser')
    table = soup_response.find("table", id = tableid).find('tbody')
    rows = table.find_all('tr', style = re.compile(r'background-color:#EAF7D5|background-color:#F0F0F0|""'))
    global_info = []
    for row in rows:
        columns = row.find_all('td')
        country_info = [column.text.strip() for column in columns]
        global_info.append(country_info)
    del global_info[:7]
    variables = ['Number','Country','Total Cases', 'New Cases','Total Deaths','New Deaths','Total Recovered', 'New Recovered','Active Cases','Serious Critical','Tot Cases/1M pop','Death/1M pop','Total Tests','Tests/1M pop','Population','Country Region','','','','','',''] 
    dataframe = pd.DataFrame(global_info, columns = variables)
    dataframe.drop(dataframe.iloc[:,[16,17,18,19,20,21]],axis=1,inplace=True)
    return dataframe '''
st.code(webscrappingcode,language="python")

st.write('Setelah melakukan webscrapping, kemudian memasuk proses data cleaning sehingga menghasilkan output datafram terakhir sebagai berikut:')
st.write('Data Dimension: ' + str(len(dftoday)) + ' rows and ' + str(len(dftoday.columns)) + ' columns.')
st.dataframe(dftoday)

# Sidebar
st.sidebar.header('Ketahui Kondisi Negaramu saat ini')
st.sidebar.subheader('Dengan memilih negaramu lewat drop-box dibawah ini, maka anda dapat mengetahui informasi negaramu')
option = st.sidebar.selectbox('Negara',dftoday.sort_values(by=['Country'])['Country'])
col1,col2 = st.sidebar.columns([0.75, 0.25])
with col1:
    st.write('**Total Kasus**')
    st.write('**Total Kematian**')
    st.write('**Total Sembuh**')
    st.write('**Jumlah Kasus Baru**')
    st.write('**Jumlah Kematian Baru**')
    st.write('**Jumlah Sembuh Baru**')
with col2:
    totalcases = int(str(dftoday[dftoday['Country']==option]['Total Cases'].squeeze()))
    totaldeaths = int(dftoday[dftoday['Country']==option]['Total Deaths'].squeeze())
    totalrecovers = int(dftoday[dftoday['Country']==option]['Total Recovered'].squeeze())
    newcases =int(str(dftoday[dftoday['Country']==option]['New Cases'].squeeze()))
    newdeaths =int(dftoday[dftoday['Country']==option]['New Deaths'].squeeze())
    newrecovers = int(dftoday[dftoday['Country']==option]['New Recovered'].squeeze())
    st.write(f'{totalcases:,}')
    st.write(f'{totaldeaths:,}')
    st.write(f'{totalrecovers:,}')
    st.write(f'{newcases:,}')
    st.write(f'{newdeaths:,}')
    st.write(f'{newrecovers:,}')
# Analisis Data
st.subheader("2. Analisis Data")
st.write('Analisis data yang dilakukan memiliki perspektif yang berbeda pada tiap orang tergantung informasi apa yang ingin diperoleh dari data tersebut. Pertama-tama, penulis memvisualisasi jumlah kasus COVID-19 disetiap negara lewat plot dibawah ini.')

# Geoplot Data Covid peta Dunia
geoscope = st.selectbox('Projection Scope', ('world','europe','asia','africa','north america','south america'))
projectiontype = st.selectbox('Projection Type', ('equirectangular', 'mercator', 'orthographic', 'natural earth','kavrayskiy7', 'miller', 'robinson', 'eckert4', 'azimuthal equal area', 'azimuthal equidistant', 'conic equal area', 'conic conformal','conic equidistant', 'gnomonic', 'stereographic', 'mollweide', 'hammer','transverse mercator', 'albers usa', 'winkel tripel', 'aitoff', 'sinusoidal'))
countrycode = pd.read_csv('Country.csv',sep=';')
dftodaywithcountrycode = pd.merge(dftoday, countrycode, on='Country')
figworld = px.choropleth(dftodaywithcountrycode, locations="Alpha Code 3",scope = geoscope,projection = projectiontype,color="Total Cases", hover_name="Country", color_continuous_scale='viridis_r')
hexcode = 0
borders=[hexcode for x in range(len(dftodaywithcountrycode))]
figworld.update_traces(marker_line_width=borders)
st.plotly_chart(figworld)

# Analisis geoplot
st.write('Berdasarkan Geoplot yang ditampilkan menggunakan library plotly bisa didapatkan informasi berupa:')
st.write('''
* Persebaran COVID-19 pada benua **Afrika** memiliki jumlah kasus dengan warna parameter dominan berwarna kuning. Secara letak geografis, dampak COVID-19 pada benua Afrika lebih sedikit.
* Persebaran COVID-19 pada benua **Eropa** memiliki jumlah kasus dengan warna parameter dominan berwarna hijau. Secara letak geografis, dampak COVID-19 pada benua Eropa cukup banyak bahkan hampir rata-rata negara total kasusnya melewati 15 juta.
* Persebaran COVID-19 pada benua **Amerika** memiliki jumlah kasus dengan warna parameter dominan berwarna hijau. Secara letak geografis, dampak COVID-19 pada benua Amerika cukup banyak terutama Amerikat Serikat dengan warna parameter berwarna ungu yang menandakan bahwa Amerika memegang jumlah kasus terbanyak dari seluruh negara di dunia.
* Persebaran COVID-19 pada benua **Asia** memiliki jumlah kasus dengan warna parameter dominan berwarna hijau muda. Secara letak geografis, dampak COVID-19 pada benua Asia cukup kecil namun terdapat pengecualian pada Negara India karena memiliki warna parameter berwarna hijau tua yang menandakan bahwa jumlah kasus di India jauh lebih tinggi dibanding negara-negara Asia lainnya.
* Rata-rata negara maju memiliki persebaran COVID-19 dengan warna parameter hijau.''')

# Analisis Correlation Variable
st.write('Dicari korelasi antar setiap column pada tabel untuk mengetahui seberapa besar pengaruh suatu column ke column lainnya. Pada kasus ini, penulis ingin mengetahui pengaruh jumlah popopulasi dan total test COVID-19 terhadap setiap kolom numeric pada tabel. Tampilan berikut merupakan heatmap plot yang menunjukan korelasi antara populasi dan total test dengan semua variable lainnya.')
worldarr = dftodaywithcountrycode.drop(['Numeric'],axis=1).corr().to_numpy()
worldarr1 = np.delete(worldarr,[0,1,2,3,4,5,6,8,10,11,12],0)
figcorr = px.imshow(worldarr1, aspect="auto", y = dftodaywithcountrycode.drop(dftodaywithcountrycode.columns[[0,1,2,3,4,5,6,7,9,11,12,13,14,15,16,17]], axis=1).columns, x = dftodaywithcountrycode.drop(dftodaywithcountrycode.columns[[0,11,15,16,17]], axis=1).columns, color_continuous_scale='Agsunset')
st.plotly_chart(figcorr)
st.write('Hasil dari plot didapatkan bahwa populasi tidak memiliki korelasi yang dikategorikan kuat banget dengan setiap variabel. Ini menandakan bahwa data populasi bukan merupakan informasi yang perlu diprioritas dalam penanganan COVID-19. Jumlah test ternyata memiliki korelasi yang kuat dengan total kasus, total kematian, dan total sembuh. Informasi yang bisa didapatkan bahwa semakin banyak fasilitas test yang disediakan oleh suatu negara, semakin terlihat seberapa besar kondisi penyebaran COVID-19 di negara tersebut. Jika dihubungkan pada analisis lokasi geografis sebelum maka bisa didapatkan bahwa hampir rata-rata negara maju pada benua Eropa memiliki angka kasus yang tinggi dibanding benua lainnya, hal itu dikarenakan negara maju memiliki fasilitas testing COVID-19 yang lebih baik dibanding negara-negara berkembang. Argumen ini dapat dibuktikan pada plot dibawah.')

#Region plot
regionplot = dftoday.groupby('Country Region')['Total Cases'].sum().drop(index='',axis=0)
regionplot = regionplot.reset_index(drop=False)
figregion = px.treemap(data_frame = regionplot,path=['Country Region'] ,values='Total Cases')
st.write(figregion)

#Cases rate plot
st.write('Apabila ditinjau dari segi kematian per total kasus, maka diperoleh geoplot seperti berikut.')
dfcasesrate = dftoday[['Country','Total Cases','Total Deaths']]
dfcasesrate['Deaths/Cases'] = dfcasesrate['Total Deaths'] / dfcasesrate['Total Cases']
dfcasesratecode = pd.merge(dfcasesrate, countrycode, on='Country')
figworld1 = px.choropleth(dfcasesratecode, locations="Alpha Code 3",color="Deaths/Cases", hover_name="Country", color_continuous_scale='Hot_r')
hexcode = 0
borders=[hexcode for x in range(len(dfcasesratecode))]
figworld1.update_traces(marker_line_width=borders)
st.plotly_chart(figworld1)
st.write('Faktor geografis tidak memiliki pengaruh yang begitu signifikan sehingga pencegahan kematian per total kasus setiap negara dipengaruhi faktor lain yang tidak dapat dianalisa pada aplikasi ini.')


#Kesimpulan
st.subheader("3. Kesimpulan")
st.write('''
1. Faktor jumlah testing COVID-19 sangat berpengaruh besar dalam penanganan COVID-19 suatu negara. Semakin banyak testing yang dilakukan, semakin banyak kasus yang diidentifikasi sehingga pasien dapat diberikan treatment untuk mengontrol angka kematian dan penyebaran yang terjadi.
2. Semakin maju sebuah negara, semakin maju fasilitas testing COVID-19 dan penanganannya. Dibuktikan lewat angka kasus yang teridentifikasi kebanyakan berada di Benua Eropa dan Amerika Utara yang mana Benua tersebut merupakan tempat didominasi negara-negara maju. Sangat terlihat jika faktor testing memberikan peran besar kepada penanganan COVID-19.
3. Populasi nyatanya tidak memiliki pengaruh besar dalam penyebaran COVID-19 dibuktikan lewat data korelasi hampir korelasi populasi dengan semua variabel tidak ada yang melewati 0,5.
4. Pengontrolan angka kematian per kasus terburuk sejauh ini masih berada pada negara Yemen dengan angka kematian sebesar ±18% 
5. Aplikasi ini masih membutuhkan variabel lain yang berisi data negara seperti ekonomi, sosial, budaya, politik, dan sumber daya alam supaya informasi yang didapatkan lewat analisis lebih  banyak dan akurat
         ''')