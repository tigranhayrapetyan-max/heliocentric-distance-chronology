# Control-case գործարկում Windows-ում

Այս release candidate-ում `RUN_CONTROL_CASE_WINDOWS.bat`-ը JPL Horizons-ի discrete `TLIST` հարցումները բաժանում է առավելագույնը 64 ժամանակակետ պարունակող խմբերի։ Սա շրջանցում է գործնականում դիտված մասնակի պատասխանը, երբ 731 հարցված ժամանակակետից վերադարձվում էին միայն առաջին 80-ը։

Գործարկեք միայն՝

```bat
RUN_CONTROL_CASE_WINDOWS.bat
```

Հաջող ավարտի դեպքում պատուհանի վերջում կերևա `CONTROL CASE PASSED.` և `outputs\control` պանակում կստեղծվեն root CSV-ները, JSON validation-ը և log-ը։
