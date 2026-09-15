import re
import csv
import os
import string

# ============================================================
# STEP 1: LOAD NORMALIZATION DICTIONARY dari normalization.csv
# ============================================================

def load_normalization_dict(csv_path: str = "./file/normalization.csv") -> tuple[dict, set]:
    """
    Membaca file normalization.csv dan membuat:
    - norm_dict : {word -> answer}  untuk normalisasi slang/singkatan
    - noise_set : {word}            untuk kata yang harus DIHAPUS dari teks
                                    (karena answer-nya adalah <noise>)
    """
    norm_dict = {}
    noise_set = set()

    if not os.path.exists(csv_path):
        print(f"[WARNING] '{csv_path}' not found. Skipping normalization step.")
        return norm_dict, noise_set

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word   = row.get('word', '').strip().lower()
            answer = row.get('answer', '').strip()

            if not word:
                continue

            answer_normalized = answer.lower().replace(' ', '')
            if answer_normalized == '<noise>':
                noise_set.add(word)
            elif answer:
                norm_dict[word] = answer.lower()

    return norm_dict, noise_set


# ============================================================
# STEP 2: INDIVIDUAL CLEANING FUNCTIONS
# ============================================================

def case_folding(text: str) -> str:
    """Lowercase semua teks."""
    return text.lower()


def remove_urls(text: str) -> str:
    """Hapus URL (http/https/www)."""
    return re.sub(r'https?://\S+|www\.\S+', '', text, flags=re.IGNORECASE)


def remove_hashtags(text: str) -> str:
    """Hapus #hashtag."""
    return re.sub(r'#\w+', '', text)


def remove_mentions(text: str) -> str:
    """Hapus @mention."""
    return re.sub(r'@\w+', '', text)


def remove_emojis(text: str) -> str:
    """Hapus emoji dan karakter unicode non-standar."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002500-\U00002BEF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d\u23cf\u23e9\u231a\ufe0f\u3030"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


def remove_noise_tags(text: str) -> str:
    """
    Hapus token literal '<noise>' atau '< noise >' yang mungkin
    muncul di dalam teks input mentah.
    """
    return re.sub(r'<\s*noise\s*>', '', text, flags=re.IGNORECASE)


def remove_punctuation(text: str) -> str:
    """
    Hapus tanda baca standar ASCII dan karakter tipografi unicode umum.
    Angka tetap dipertahankan.
    """
    # Tanda baca ASCII standar
    ascii_punct = string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

    # Tanda baca unicode tambahan yang sering muncul di teks sosmed
    unicode_punct = '…""''–—•·«»°×÷©®™'

    all_punct = ascii_punct + unicode_punct
    return text.translate(str.maketrans('', '', all_punct))


def remove_extra_whitespace(text: str) -> str:
    """Bersihkan spasi berlebih dan strip."""
    return re.sub(r'\s+', ' ', text).strip()


# ============================================================
# STEP 3: NORMALIZATION + HAPUS NOISE WORDS
# ============================================================

def normalize_text(text: str, norm_dict: dict, noise_set: set) -> str:
    """
    Per kata:
    - Jika kata ada di noise_set → HAPUS (tidak dimasukkan ke hasil)
    - Jika kata ada di norm_dict → GANTI dengan bentuk baku
    - Selainnya                  → biarkan

    Catatan: remove_punctuation() dipanggil sebelum fungsi ini,
    sehingga tidak perlu lagi strip tanda baca di tepi kata.
    """
    if not norm_dict and not noise_set:
        return text

    words = text.split()
    result = []
    for word in words:
        if word in noise_set:
            continue
        elif word in norm_dict:
            result.append(norm_dict[word])
        else:
            result.append(word)

    return ' '.join(result)


# ============================================================
# STEP 4: TOKEN PREVIEW (untuk UI info)
# ============================================================

def get_token_preview(text: str, tokenizer) -> dict:
    """Preview tokenisasi untuk ditampilkan di UI."""
    tokens  = tokenizer.tokenize(text)
    encoded = tokenizer.encode(text, truncation=True, max_length=512)
    return {
        "tokens"      : tokens,
        "token_count" : len(encoded),
        "truncated"   : len(encoded) >= 512
    }


# ============================================================
# STEP 5: FULL PIPELINE
# ============================================================

def preprocess(text: str, norm_dict: dict, noise_set: set) -> str:
    """
    Pipeline preprocessing lengkap sebelum masuk model:

    1. Case Folding        → semua huruf kecil
    2. Remove URLs         → hapus http/https/www
    3. Remove Hashtags     → hapus #hashtag
    4. Remove Mentions     → hapus @mention
    5. Remove Emojis       → hapus karakter emoji & unicode non-standar
    6. Remove Noise Tags   → hapus token literal <noise>
    7. Remove Punctuation  → hapus tanda baca ASCII & unicode tipografi
    8. Normalize + Noise   → ganti slang via normalization.csv,
                             HAPUS kata yang answer-nya <noise>
    9. Whitespace Cleanup  → rapikan spasi

    Returns:
        Teks bersih siap dimasukkan ke tokenizer & model.
    """
    text = case_folding(text)
    text = remove_urls(text)
    text = remove_hashtags(text)
    text = remove_mentions(text)
    text = remove_emojis(text)
    text = remove_noise_tags(text)
    text = remove_punctuation(text)
    text = normalize_text(text, norm_dict, noise_set)
    text = remove_extra_whitespace(text)
    return text


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    samples = [
        "Gw bgt gabut hari ini 😭 #mondaymood @temanku cek https://t.co/abc123",
        "mangamanhwadonghuavtuberstreamergame bikin distraksi banget",
        "aku lagi <noise> sedih bgt < noise > hari ini",
        "wkwkwkwkkwkwkwkwkwkwkwkwkw lucu juga sih",
        "kmrn ketemu doi trs skrg ghosting wtf 😤 #galau",
        'dia bilang "gapapa" tapi mukanya... 💔',
        "harga naik 10%!!! gila banget sih—nggak masuk akal.",
    ]

    norm_dict, noise_set = load_normalization_dict("./file/normalization.csv")
    print(f"[INFO] norm_dict: {len(norm_dict)} entries | noise_set: {len(noise_set)} entries\n")

    for i, text in enumerate(samples, 1):
        result = preprocess(text, norm_dict, noise_set)
        print(f"[{i}] ORIGINAL : {text}")
        print(f"    CLEANED  : {result}")
        print()