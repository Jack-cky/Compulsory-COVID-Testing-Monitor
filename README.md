# Dragon Tiger Billboard — Rankings of Building on Compulsory COVID Test in Hong Kong
<p align="center">
    <a href="https://www.chp.gov.hk/files/pdf/ctn.pdf"><img src="https://github.com/Jack-cky/DTB-Rankings_of_Building_on_Compulsory_COVID_Test/blob/main/imgs/community_testing.png"></a><br>
    <i> Credit: <a href="https://www.info.gov.hk/gia/general/202202/10/P2022021000374.htm"> info.gov.hk </a></i>
</p>

Click [me](https://public.tableau.com/app/profile/jackcky/viz/HongKongCompulsoryTestingNoticeDragonTigerBillboard/DTB) to travel Tableau dashboard!

---
### Background
- Under the pandemic of COVID-19, the Hong Kong Government (HKG) tries to achieve "Dynamic Zero Infection" by introducing vaccine passports to encourage the public to get vaccinated.
- In addition, the HKG exercises the power of the Prevention and Control of Disease Ordinance (Chapter 599) to require the public to undergo a COVID-19 nucleic acid test if they had been present at one specified premise.
- Earlier we found an interesting [post](https://forum.hkgolden.com/thread/7600216/page/1) in HKGolden discussing the annoyance of the Compulsory Testing Notice (CTN) and looking for a Dragon Tiger Billboard (a.k.a. 龍虎榜 in Chinese or ranking billboard in English) to see which buildings appeared on the CTN the most.
- Unfortunately, there is no such official publication for the ranking on the CTN. We were inspired by the idea and kicked started the project of building a Dragon Tiger Billboard to dashboardise the frequency of specified premises being listed on the CTN.

---
### Dashboard Demo
<p align="center"><a href="https://public.tableau.com/app/profile/jackcky/viz/HongKongCompulsoryTestingNoticeDragonTigerBillboard/DTB"><img src="https://github.com/Jack-cky/DTB-Rankings_of_Building_on_Compulsory_COVID_Test/blob/main/imgs/dashboard_demo.gif"></a></p>

---
### Data Source
For the absence of tabular data on CTN, data is drawn from [PDF files](https://www.chp.gov.hk/en/features/105294.html) available on the Centre for Health Protection (CHP). External data, such as geocoding of addresses, will be extracted as well. Data processing is done in Python scripting.

---
### Project Implementation
1. Download CTNs from the CHP for the start of the project.
    -  CTNs are captured since 14 January 2022 due to inconsistent table format
    -  Up-to-date CTN records with 31 August 2022
2. Extract information from PDFs for building a data model.
    -  For configuration of dependency, only column "指明地點 Specified place" will be ingested
    -  Places with a typo or without a [sub-district](https://www.rvd.gov.hk/doc/tc/hkpr15/06.pdf) will be removed
    -  Geographic information of given addresses is referenced by [Hong Kong Address Parser](https://github.com/chunlaw/HKAddressParser)
3. Save the output acting as a data source for the dashboard.
4. Build a Dragon Tiger Billboard for dashboarding frequency of specified premises.
<p align="center"><a href="https://github.com/Jack-cky/DTB-Rankings_of_Building_on_Compulsory_COVID_Test/tree/main/src"><img src="https://github.com/Jack-cky/DTB-Rankings_of_Building_on_Compulsory_COVID_Test/blob/main/imgs/project_implementation.png"></a></p>

---
### Dashboard Explanation
<p align="center"><a href="https://public.tableau.com/app/profile/jackcky/viz/HongKongCompulsoryTestingNoticeDragonTigerBillboard/DTB"><img src="https://github.com/Jack-cky/DTB-Rankings_of_Building_on_Compulsory_COVID_Test/blob/main/imgs/dashboard_explanation.png"></a></p>

---
### Acknowledgements
- The dashboard design is stolen from [Homework Dragon Tiger Billboard](https://hodao.edu.hk/CustomPage/131/2020-2021_05月份交齊功課龍虎榜.jpg) by Ho Dao College.
- Usage of Tabula-py is referenced from [here](https://aegis4048.github.io/parse-pdf-files-while-retaining-structure-with-tabula-py) which introduces the framework usage in detail.
