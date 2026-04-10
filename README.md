# Lietuvos degalų kainų žemėlapis

## Išbandyk: https://ltlukoziuzu.github.io/degaline-zemelapis/

## AI Disclaimer'is
Taip, nors ir nelabai norom, bet šis projektas yra pilnai sukonstruotas su Claude Code CLI. Web'o žinios pas mane ganėtinai minimalios (per paskutinius 12 metų tik su Unity (C#) lengvai programuota, daugiau tik ką pastebiu iš savo patirties kaip manual QA), lengvus edit'us galiu daryt, bet nesukonstruot viską nuo nulio. Vienintelė didesnė išimtis - šis readme failas. Paprašiau, kad tik duotų initial layout'ą, bet toliau viskas parašyta ranka.

## Apie projektą
<sub>*Famous last words:* </sub>  
<sub>*tik atsiradus LEA duomenims* "nu, kiek greitai kas nors padarys automatiškai žemėlapis kad updatintųs pagal duomenis čia?" </sub>  
<sub>*sekančią dieną* "well, close enough, 15min, albeit tėvams nebūtų useful, nes [15min](https://cdn.imgchest.com/files/cc4f0e6ca03d.png) manymu, "šalia tavęs" yra 10km spinduliu, kai Šiauliai 20+ km away 😄"</sub>  
<sub>*po dešimt minučių* "now wondering kiek stupid idea būtų pačiam kažką su vibe codint (and how to do it) XD"</sub>

Idėja paprasta - padaryti interaktyvų žemėlapį, kuriame greitai galėtų pažiūrėti bet kokios vietovės (pagal vartotojo lokaciją, pagal tašką arba pagal pasirinktą degalinę) pigiausias vertes. Žemėlapis pats reguliariai (LEA darbo valandomis) ištraukia naujus duomenis ir juos pakeičia, jei randama naujų adresų, juos cache'ina, kad vieši API būtų neapkrauti. 

**Pastaba:** Kadangi degalinių yra 725 šio dokumento rašymo metu, ne visos yra ranka patikrintos, ar pataiko į koordinates - photon.komoot.io kartais kiek klysta. Pagrindinės klaidos ištaisytos (23 adresus ne Lietuvoje rado - kaltinkit degalinių tinklus, kaip kreivai jie surašo adresus, ne pagal taip kaip visi žemėlapiai tikisi), bet dėl šventos ramybės reiktų visus pereiti. Pasidarytas įrankis padaryti tai po truputį, netrukdant svetainės kūrimui ir naudojimui.

## Kaip naudotis
Trys būdai, kaip galima ieškoti atstume aplink:
* Pagal vartotojo lokaciją: Apatiniame kairiajame kampe mygtukas. Pirma bandoma rasti vartotojo lokaciją pagal GPS, jei duodamas leidimas. Jei nutinka klaida ar neduodamas leidimas, vietoj to rodoma apytikslė vieta pagal matomą IP adresą.
* Pagal pasirinktą degalinę: Pasirinkus degalinę iš paieškos ar žemėlapio, atsiranda mygtukas "Rasti pigesnes netoliese"
* Pagal pasirinktą tašką: Viršuje dešinėje mygtukas, kurį paspaudus vartotojas gali pasirinkti bet kurį tašką žemėlapyje

Bet kokiu atveju, pasirinkus kuro tipą bei atstumą, parodomos trys pigiausios degalinės. Jeigu ieškoma pagal pasirinktą degalinę, pirmas variantas vietoje pigiausios apskritai rodo pigiausią tame tinkle - jei vartotojas turi lojalumo kortelę/kitų nuolaidų ar tiesiog nori tam tikro tinklo.

Duomenis atnaujina pati svetainė, grubiai kas 15 minučių LEA darbo valandomis (Github Actions kartais užtempia runner'io paleidimą) iki kol randamas šiandienos failas - po radimo ir visų veiksmų su juo atlikimo tolimesni patikrinimai iškart sustoja.

## Duomenų šaltinis
Kainų duomenys: [Lietuvos Energetikos Agentūra (LEA)](https://www.ena.lt/degalu-kainos-degalinese/) ir degalinių tinklai, suteikę jai informaciją

Geocache: Sudarytas su [photon.komoot.io](https://photon.komoot.io/) API (jo duomenys iš [OpenStreetMap](https://www.openstreetmap.org/))

Adreso paieška pagal IP: [ipinfo.io](https://ipinfo.io/)
