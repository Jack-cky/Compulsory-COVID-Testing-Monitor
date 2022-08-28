# Dragon Tiger Billboard — (Hong Kong) Compulsory Testing Notice

Link to Tableau dashboard:
- [(Hong Kong) Compulsory Testing Notice — Dragon Tiger Billboard](https://public.tableau.com/app/profile/jackcky/viz/HongKongCompulsoryTestingNoticeDragonTigerBillboard/DTB)

---
### _**Background**_
- Under the pandemic of COVID-19, the Hong Kong Government (HKG) tried to achieve "Dynamic Zero Infection" by introducing vaccine passports to encourage the public to get vaccinated.
- In addition, the HKG exercises the power of the Prevention and Control of Disease Ordinance (Chapter 599) to require the public who had been present at one specified premise to undergo a COVID-19 nucleic acid test.

---
### _**Motivation**_
- Earlier we saw a [post](https://forum.hkgolden.com/thread/7600216/page/1) in HKGolden, discussing the policy of the Compulsory Testing Notice (CTN) that annoyed some groups of people. It is true that the policy is quite disturbing for we have been tested 3 times over the past few months.
- There is no official publication about the CTN statistics. It seems to be interesting to know which buildings have been tested the most under the policy. Using the dragon tiger billboard gives us a quick review of the figures and spots out the top testing buildings.

---
### _**Project Workflow**_
1. Download [CTN](https://www.chp.gov.hk/en/features/105294.html) from the Centre for Health Protection.
2. Work on CTN to extract "Specified Place" information.
3. Save the results as the data model.
4. Build the dragon tiger billboard.

![project_flow](imgs/project_flow.png)

---
### _**Assumption**_
- CTN are captured since 14 January 2022 for consistent records.
- Due to the PDF table extraction limit, only column "指明地點 Specified place" will be used.
- Only consider specified places with a valid address, which ignored addresses without sub-districts or with a typo.
- Geographic information heavily rely on the results given by `Hong Kong Address Parser`.

---
### _**Dashboard Demo**_
![dashboard_demo](imgs/dashboard_demo.gif)

---
### _**References**_
- [有冇網統計強檢龍虎榜](https://forum.hkgolden.com/thread/7600216/page/1)
- [COVID-19 - Lists of Specified Premises of Compulsory Testing Notices](https://www.chp.gov.hk/en/features/105294.html)
- [Parse PDF Files While Retaining Structure with Tabula-py](https://aegis4048.github.io/parse-pdf-files-while-retaining-structure-with-tabula-py)
- [Areas and Districts](https://www.rvd.gov.hk/doc/tc/hkpr15/06.pdf)
- [Hong Kong Address Parser](https://github.com/chunlaw/HKAddressParser)
- [2020-2021_05月份交齊功課龍虎榜](https://hodao.edu.hk/CustomPage/131/2020-2021_05月份交齊功課龍虎榜.jpg)