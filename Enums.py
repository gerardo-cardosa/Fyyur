from enum import Enum

class StatesEnums(Enum):
    AL='AL'
    AK='AK'
    AZ='AZ'
    AR='AR'
    CA='CA'
    CO='CO'
    CT='CT'
    DE='DE'
    DC='DC'
    FL='FL'
    GA='GA'
    HI='HI'
    ID='ID'
    IL='IL'
    IN='IN'
    IA='IA'
    KS='KS'
    KY='KY'
    LA='LA'
    ME='ME'
    MT='MT'
    NE='NE'
    NV='NV'
    NH='NH'
    NJ='NJ'
    NM='NM'
    NY='NY'
    NC='NC'
    ND='ND'
    OH='OH'
    OK='OK'
    OR='OR'
    MD='MD'
    MA='MA'
    MI='MI'
    MN='MN'
    MS='MS'
    MO='MO'
    PA='PA'
    RI='RI'
    SC='SC'
    SD='SD'
    TN='TN'
    TX='TX'
    UT='UT'
    VT='VT'
    VA='VA'
    WA='WA'
    WV='WV'
    WI='WI'
    WY='WY'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.value) for choice in cls]


class GenreEnums(Enum):
    Alternative='Alternative'
    Blues='Blues'
    Classical='Classical'
    Country='Country'
    Electronic='Electronic'
    Folk='Folk'
    Funk='Funk'
    Hip_Hop='Hip-Hop'
    Heavy_Metal='Heavy Metal'
    Instrumental='Instrumental'
    Jazz='Jazz'
    Musical_Theatre='Musical Theatre'
    Pop='Pop'
    Punk='Punk'
    R_B='R&B'
    Reggae='Reggae'
    Rock_n_Roll='Rock n Roll'
    Soul='Soul'
    Other='Other'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.value) for choice in cls]
    
    @classmethod
    def choicesSingle(cls):
        return [choice.value for choice in cls]
