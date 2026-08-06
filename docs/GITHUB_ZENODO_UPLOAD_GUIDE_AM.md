# GitHub և Zenodo վերբեռնման քայլերը

## Ներկա փաթեթի կարգավիճակը

Workbook-ը, սկզբնական վիճակագրական script-ը, CSV root catalogue-ները և վերարտադրված վիճակագրական արդյունքները արդեն ներառված են։ Ներկա տարբերակը `v0.9.1 release candidate` է, քանի որ NASA/JPL Horizons control case-ը և ամբողջական root regeneration-ը դեռ պետք է գործարկել ինտերնետ հասանելի Windows համակարգչում։

## 1. Սկզբնական ստուգում համակարգչում

1. Բացել ZIP-ը առանձին պանակում։
2. Կրկնակի սեղմել `RUN_STATISTICAL_VALIDATION_WINDOWS.bat`։
3. Ստուգել, որ արդյունքները ցույց տան՝ 7,863 / 447 / 42 root, conditional proportion `0.001607873066...`, Monte Carlo `1649/1,000,000` և 5 անցած test։
4. Կրկնակի սեղմել `RUN_CONTROL_CASE_WINDOWS.bat`։
5. Արդյունքը պետք է պահպանվի `outputs/control/control_case_validation.json` ֆայլում և ունենա `overall_status: pass`։

## 2. GitHub repository

1. Մուտք գործել GitHub և սեղմել **New repository**։
2. Անվանում՝ `heliocentric-distance-chronology`։
3. Visibility՝ **Public**։
4. Չավելացնել ավտոմատ README կամ license։
5. Վերբեռնել բացված repository պանակի ամբողջ պարունակությունը, ոչ արտաքին ZIP-ը։
6. `CITATION.cff` ֆայլում `REPLACE_WITH_GITHUB_USERNAME`-ը փոխարինել իրական GitHub username-ով։
7. Commit message՝ `Initial public release candidate v0.9.1`։

## 3. Ո՞ր version-ը հրապարակել

- Եթե միայն վիճակագրական reproduction-ն ու disclosed catalogue-ն են ստուգված, ստեղծել GitHub release/tag՝ `v0.9.1`։
- Եթե control case-ը, ամբողջ 7,863 / 447 / 42 root regeneration-ը և root-by-root comparison-ը անցել են, metadata-ն փոխել `1.0.0` և ստեղծել `v1.0.0` release։

## 4. Zenodo կապում GitHub-ին

1. Մուտք գործել Zenodo նույն GitHub account-ով։
2. Zenodo-ի GitHub settings-ում միացնել repository-ն։
3. GitHub-ում ստեղծել համապատասխան release (`v0.9.1` կամ `v1.0.0`)։
4. Zenodo-ն ավտոմատ կստեղծի draft record։
5. Metadata-ի համար օգտագործել `docs/ZENODO_METADATA_COPYPASTE.md`։
6. Ստուգել creator, ORCID, affiliation, license, version և description։
7. Սեղմել **Publish** և ստացված DOI-ն ուղարկել ChatGPT-ին՝ երկու ձեռագրերի մեջ տեղադրելու համար։

## 5. Երկու հոդվածների միաժամանակյա հանձնում

Երկու cover letter-ներում նշել, որ դրանք companion manuscripts են և օգտագործում են նույն Zenodo-արխիվացված computational research object-ը, բայց ունեն տարբեր հետազոտական հարցեր, մեթոդաբանական դերեր և եզրակացություններ։
