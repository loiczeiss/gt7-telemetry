"""GT7 car-code catalog and lookup helpers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CarInfo:
    name: str
    manufacturer_id: int


# IDs are the values sent by GT7 at CAR_CODE_OFFSET.
# Keep this mapping data-only so the complete supplied catalog can be extended
# without changing the session workflow.
CAR_CATALOG: dict[int, CarInfo] = {
    24: CarInfo("180SX Type X '96", 28),
    31: CarInfo("Camaro Z28 '69", 7),
    36: CarInfo("Chevelle SS 454 Sport Coupe", 7),
    41: CarInfo("Corvette Stingray (C3) '69", 7),
    48: CarInfo("Fairlady 240ZG (HS30) '71", 28),
    63: CarInfo("Corolla Levin 1600GT APEX (AE86) '83", 43),
    82: CarInfo("Supra RZ '97", 43),
    116: CarInfo("GT-One (TS020) '99", 43),
    135: CarInfo("S800 '66", 15),
    137: CarInfo("Beat '91", 15),
    203: CarInfo("Integra Type R (DC2) '98", 15),
    204: CarInfo("Civic Type R (EK) '98", 15),
    205: CarInfo("RX-7 Spirit R Type A (FD) '02", 21),
    210: CarInfo("R34 GT-R V-spec II Nur '02", 28),
    216: CarInfo("McLaren F1 GTR Race Car '97", 6),
    293: CarInfo("NSX Type R '92", 15),
    296: CarInfo("787B '91", 21),
    315: CarInfo("Cobra 427 '66", 36),
    365: CarInfo("155 2.5 V6 TI '93", 3),
    374: CarInfo("RX-7 GT-X (FC) '90", 21),
    379: CarInfo("Impreza Coupe WRX Type R STi Ver.VI '99", 38),
    387: CarInfo("300 SL Coupe '54", 22),
    396: CarInfo("NSX Type R '02", 15),
    451: CarInfo("Impreza 22B-STi '98", 38),
    514: CarInfo("S2000 '99", 15),
    533: CarInfo("Stratos '73", 18),
    604: CarInfo("2000GT '67", 43),
    665: CarInfo("Superbird '70", 55),
    773: CarInfo("R32 GT-R V-spec II '94", 28),
    779: CarInfo("Cappuccino (EA11R) '91", 39),
    808: CarInfo("V6 Escudo Pikes Peak Special spec.98", 39),
    810: CarInfo("Sprinter Trueno 1600GT APEX (AE86) '83", 43),
    1040: CarInfo("Ford GT LM Race Car Spec II", 13),
    1365: CarInfo("R8 4.2 '07", 5),
    1378: CarInfo("F430 '06", 110),
    1409: CarInfo("F40 '92", 110),
    1426: CarInfo("Ford GT '06", 13),
    1484: CarInfo("Countach LP400 '74", 112),
    1504: CarInfo("458 Italia '09", 110),
    1507: CarInfo("SLS AMG '10", 153),
    1536: CarInfo("Zonda R '09", 30),
    1562: CarInfo("LFA '10", 50),
    1722: CarInfo("MP4-12C '10", 117),
    1770: CarInfo("Aventador LP 700-4 '11", 112),
    1797: CarInfo("SLS AMG GT3 '11", 153),
    1905: CarInfo("GT-R NISMO GT3 '13", 28),
    2049: CarInfo("Veyron 16.4 '13", 113),
    2050: CarInfo("Huayra '13", 30),
    2077: CarInfo("Red Bull X2014 Standard", 33),
    2108: CarInfo("SRT Tomahawk X VGT", 11),
    2149: CarInfo("Mercedes-AMG GT S '15", 153),
    2159: CarInfo("Mustang Gr.3", 13),
    2160: CarInfo("Genesis Gr.3", 16),
    2161: CarInfo("GT-R Gr.4", 28),
    2183: CarInfo("Corvette C7 Gr.3", 7),
    3183: CarInfo("PEUGEOT VGT (Gr.3)", 32),
    3268: CarInfo("911 GT3 RS (991) '16", 136),
    3311: CarInfo("911 RSR (991) '17", 136),
    3345: CarInfo("GT-R NISMO '17", 28),
    3352: CarInfo("GR Supra Racing Concept '18", 43),
    3367: CarInfo("GR Supra RZ '19", 43),
    3418: CarInfo("GR Supra RZ '20", 43),
    3499: CarInfo("GR010 HYBRID '21", 43),
    3536: CarInfo("Civic Type R (FL5) '22", 15),
    3539: CarInfo("911 GT3 RS (992) '22", 136),
    3540: CarInfo("Model 3 Performance '23", 119),
    3553: CarInfo("GT-R Premium edition T-spec '24", 28),
    3554: CarInfo("Hiace Van DX '16", 43),
}


def get_car_info(car_code: int) -> CarInfo | None:
    return CAR_CATALOG.get(car_code)


def format_car_name(car_code: int) -> str:
    car = get_car_info(car_code)
    return car.name if car else f"Unknown (#{car_code})"
