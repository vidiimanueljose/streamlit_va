"""
predict_va.py — Batch prediction Valence-Arousal dari list kalimat, hasil disimpan ke CSV.

Pakai model_loader.py yang udah ada (load_model, VALENCE_INDEX, AROUSAL_INDEX) dan
preprocessing.py (preprocess, load_normalization_dict) biar konsisten sama sisa
aplikasi Streamlit kamu.
"""

import torch
import pandas as pd

from model_loader import load_model, VALENCE_INDEX, AROUSAL_INDEX
from preprocessing import preprocess, load_normalization_dict

MODEL_PATH = "./model"
NORM_CSV_PATH = "./file/normalization.csv"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def predict_texts(
    texts: list[str],
    output_csv: str = "predictions.csv",
    batch_size: int = 16,
) -> pd.DataFrame:
    """
    texts       : list kalimat yang mau diprediksi
    output_csv  : path file csv output
    """
    tokenizer, model = load_model(MODEL_PATH)
    norm_dict, noise_set = load_normalization_dict(NORM_CSV_PATH)
    model.to(DEVICE)
    model.eval()

    pred_valences, pred_arousals = [], []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]

        # preprocessing: lexicon substitution + cleaning (emoji/url/hashtag/dll)
        cleaned = [preprocess(t, norm_dict, noise_set) for t in batch_texts]

        encoded = tokenizer(
            cleaned,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt",
        ).to(DEVICE)

        with torch.no_grad():
            outputs = model(**encoded)

        # XLMRRegression.forward() return dict biasa: {"loss": ..., "logits": tensor}
        # (bukan object HF yang punya atribut .logits), jadi harus dicek dulu
        # apakah dict/mapping (pakai key) atau punya atribut .logits, baru fallback ke tensor langsung.
        if isinstance(outputs, dict):
            logits = outputs["logits"]
        elif hasattr(outputs, "logits"):
            logits = outputs.logits
        else:
            logits = outputs

        batch_valence = logits[:, VALENCE_INDEX].detach().cpu().numpy()
        batch_arousal = logits[:, AROUSAL_INDEX].detach().cpu().numpy()

        pred_valences.extend(batch_valence.tolist())
        pred_arousals.extend(batch_arousal.tolist())

    df = pd.DataFrame({
        "text": texts,
        "valence": pred_valences,
        "arousal": pred_arousals,
    })

    df.to_csv(output_csv, index=False)
    print(f"Selesai! {len(texts)} kalimat diprediksi, hasil disimpan ke '{output_csv}'")
    return df


if __name__ == "__main__":
    # ganti list ini sesuai kalimat yang mau kamu prediksi
    texts = [
        "Ngerasa nggak sih? Semakin dewasa circle makin kecil, tapi makin berharga.",
        "Ngajarin orang buat sabar dan selalu fokus sama solusi bukan sama masalahnya tuh gampang gampang susah. Apalagi orangnya keras kepala",
        "Polisi anjing, biadab bgst setan najis iblis lu. Gw udh cape gda tenaga lg mau memaki. Tp lu bgst brengsek bgt anjing. Semoga hidup lu tersiksa dunia akhirat anjing",
        "Cape banget hidup ni ya, udah live gbisa, pemerintah nya kek mana, skrng mau cari duit gimana coba, udah apamahal, malah pendapatan paling besar ditutup jugacapeeeeeeee",
        "hidup lagi cape cape nya malah lahir jadi wni",
        "semua memorinya keputer semua di otak, kalian sayang sama akuu tapi aku tetep disini sendiri hahahha anjir lucu bgt anjir hahahahha sakit bgt sakitttrrrrrrrrrr dadaku sakit bgt sialan. cape bgt dikira aku mau apa hidup kayak gini kocakkkkk mana udh 21 thn ya sekarang wkwkwk gws",
        "YaAllah kapan yaa situasi bisa tenang dan stabil kembali cape, sedih, kesel, muak, gedeg campur aduk deh ngeliat berita skrg ini gatau mau blg gmn lgiii intinyaa stay safe yaa utk semua hidup perjuangan!",
        "cape anjir hidup selalu dibawah bayangan org lain anjir anjir",
        "rasanyaa udh cape sm mnet malah dibikin kayak begini, ga bs apa ya hidup damai huft",
        "Cape, pengen nyerah. Tapi hidup berakhir juga bukan solusi",
        "cape bgt nangisin hidup gabisa live tiktok, pajak naik mulu asu, gaji naik seperak pun gabisa sial mereka dengan asiknya buat keputasan naik gaji mereka yang buat mereka yang acc bjingaannnnnnnnnn",
        "ya Allah rasanya udah cape banget. gue juga udah gaada rasa pengen hidup lagi. bisa ga langsung turunin azab aja semua.",
        "ga cuma pemerintah, tapi orang-orang yang kenal juga pada dzolim sama aku. cape banget, soalnya aku beneran cape... kenapa ya hidup sefucked up ini, padahal ga pernah tuh kepikiran mau dzolimin orang lain, ambil hak orang lain gitu ga pernah tuh kepikiran tp kok hidupku begini...",
        "namanya juga hidup yaa pasti cape tapi CAPE BANGET BANGSATTTTT",
        "huhu, sedih... tibatiba kepikiran. aku ga pernah mau dilahirkan di negara kek gini, aku salah apa ya sampe bisa hidup di negara yang penuh sama org dzolim kek gini... nangis bgt mikirinnya, kek kehidupan yang lebih baik itu, pasti ada kan? sampe kapan bakal begini... cape...",
        "Pembagian warisan dan melihat bokap dimandiin waktu itu sedih bgt. semakin cape sama dunia ini, cari apa ya? ga sedih kah bkp sdh berjuang semasa hidup, skg kayak mau balas kasih pahala supaya almarhum bisa masuk surga. Terima kasih pah, ak coba ya jd anak soleha.",
        "hidup udah cape banget jadi WNI, malah dipimpin penjabat goblokkkkkk dongo gajelas taiiiiii",
        "G prnh semuak ini sm hidup, cape bgt",
        "Hidup mode survival terus gak cape apa ya.",
        "ini hidup ngejar apasi anjing cape banget",
        "Xavibul robek robek gini demi suami laen coba ah elah cape cape hidup gini amat",
        "lu pada cape ga sih hidup selalu another life mulu?",
        "Kosan hening dong. Bayangin aja nder udah capek kerja dari pagi sampe sore, malemnya hidup lu ga tenang dengerin ortu berantem. Apa ga cape lu",
        "aku pengen hidup langsung happy ending, cape grasak grusuk mulu",
        "Sakit, cape, gw cuma pengen hidup tenang",
        "Cape hidup, tapi mati juga ga siap",
        "pgn meninggal aja pls cape hidup",
        "cape banget anjir, ngerasa ga bebas buat nikmatin hidup. MASA GUE MAU MAKAN MAKANAN YG MANIS AJA NGERASA BERSALAH BANGET SAMA KULIT GUEEE",
        "kok cape ya I mean, hidup.",
        "kirain quarter life crisis fase paling ampas di hidupku, ternyata late 20 jg sama aja ampasnya. at least dl aku punya temen deket, punya pacar, keluargaku utuh. tahun ini aku kehilangan banyak hal. masalah datang satu per satu. aku cape, aku harus hidup kaya gimana lagi.",
        "terimakasih bapak bapak sudah mau mendengarkan keluh kesah indy yg masi kicik nan bodoh ini. gabole cape ya janji harus ttp hidup lama!",
        "Gue beneran makin sini makin cape hidup",
        "sambil melewati tb simatupang, damn mau nangis ggr cape macet sama cape hidup l, beda tipis",
        "buset dah hidup udah cape kerjaan rumah kaga beres beres anjggg",
        "lagi di titik burnout dan cape sama segala hal. kerja cape, jbjb di x cape, bahkan do smthing buat perut sendiri juga kaya cape banget. hidup rasanya gaada motivasi, bingung harus berjuang dan survive untuk siapa hopeless sama keadaan padahal dulu aku punya banyak rencana hidup",
        "hidup nih ngejar apasih sebenernya? cape bgt anj",
        "jujur cape harus mulai semuanya lagi dari awal terbiasa hidup sendiri lagi",
        "Kenapa cape banget ya ngadepin hidup kek gini. Udah tua bukannya makin dewasa, bijaksana, berpola pikir matang Ini malah makin tolol anjir. DEYM",
        "awalnya tu gw bener2 orang yg pendengar, gw dg senang hati dengerin smua ceritanya smape berjam2, gw tahan ngantuk gw. tp ceritanya selalu sama, cape kerja, muak menghidupi adik2nya. gw ngerti lo cape, tp jgn cerita setiap hari ttg kecapean lo itu, KAN GW HIDUP JG CAPE",
        "gua tuh beneran ga ngerti, kenapa semuanya harus serumit ini, rasanya kaya hidup tuh ga pernah kasih gua ruang buat bener-bener lega. gua udah pernah ngerasain sakit ini, tapi sekarang rasanya lebih dalem, lebih nyakitin. cape banget selalu di posisi yang kalah dan salah",
        "walaupun disetiap tempat kerja pasti ada anomali tapi gue bersyukur akhirnya gue lepas dari kerjaan sekarang. cape dan nguras energi bgt. apalagi ada 1 anomali yg ya allah lu hidup nyusahin orng bgt",
        "berkali kali berdoa buat minta dicabut nyawa, tapi kenapa masih dikasih hidup? aku cape ya Allah",
        "Cape bgt gue breakout mulu dh ya Allah knp si Gula udh dikurangin, olahraga juga, coklat udh bener bener dicut...STRESS? KARENA STRES? CARANYA GMB BIAR G STRESS GUE TANYA??? Hidup had so much pressure on me ya, pls yq Allah..",
        "betul banget yang disalahin atasan mulu giliran diminta masukan pas meeting pada diem diem bae begitu aja terus sampe kiamat alasannya ga bakal didenger lah atau cape jadi paling speak up susah emang kalo hidup dijaman kapitalis",
        "Kapan ya gw bisa hidup kayak gtu lg. Gw bisa diem, bisa berisik, bisa salah, bisa bener, bisa puitis, bisa cuek, pokoknya no judgement, ya ada sih tp ga parah lah. Gw udh yg cape bgt deh ama hidup knp org2 keren bgt then theres me????",
        "semoga kantor ku nanti punya access transum yg memadai ya allahh, AMINN!! gua tidak bisa hidup tanpa transum jirs.. malas bgt kalo harus bawa kendaraan karena pasti cape dijalan doang itu..",
        "Cape banget hidup ya Allah. Hidup cape, mati ga siap. Gw hrs gmn lagi... Udah ga ada tenaga buat jalanin ini semua..",
        "Karena orang tua aku selalu ngelarang. Padahal itu kebahagiaan aku? Aku cape aku kadang mikir kenapa sih hidup aku banyak gak boleh nya? Padahal aku yang usaha dengan duit sendiri. Itu yang bikin aku cape aku juga lelah. Ada batasan nya",
        "Kadang ya sedih... Di hidup aku yang aku bener bener bersyukur cuma ketemu Nicholas, Ni-ki sama Minho doang... Selebihnya aku hidup kaya ngambang aja... Aku cape sama hidup aku tapi gak ada yang ngerti, padahal aku manusia yang ada kapasitas batasannya..",
        "cape banget hidup sendiri sunyi"
    ]

    predict_texts(
        texts=texts,
        output_csv="hasil_prediksi.csv",
    )