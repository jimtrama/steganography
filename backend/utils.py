from PIL import Image
from settings import UPLOAD_FOLDER
import math
def text_to_binary(string):
    return ''.join(format(byte, '08b') for byte in string.encode('utf-8'))

def binary_to_text(bin):
    complete_bytes = len(bin) - (len(bin) % 8)
    data = bytes(int(bin[i:i+8], 2) for i in range(0, complete_bytes, 8))
    return data.decode('utf-8', errors='ignore')

def text_to_length_prefixed_binary(string):
    data = string.encode('utf-8')
    length_prefix = format(len(data), '032b')
    return length_prefix + ''.join(format(byte, '08b') for byte in data)

def length_prefixed_binary_to_text(bits):
    if len(bits) < 32:
        raise ValueError("Missing message length prefix.")

    byte_length = int(bits[:32], 2)
    payload_length = byte_length * 8
    payload_start = 32
    payload_end = payload_start + payload_length

    if payload_end > len(bits):
        raise ValueError("Encoded message is incomplete.")

    payload_bits = bits[payload_start:payload_end]
    return binary_to_text(payload_bits)

def message_bits_from_payload(bits, delimiter_text="/"):
    delimiter = text_to_binary(delimiter_text)
    if delimiter in bits:
        return bits.split(delimiter, 1)[0]
    return bits

def encode(msg):
    img = Image.open(f"{UPLOAD_FOLDER}/file.png").convert("RGBA")
    width, height = img.size
    pixels = img.load()
    data_length = len(msg)
    data_index = 0
    # Increase red channel
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            # Modify R channel
            if data_index < data_length:
                r = (r & 0b11111110) | int(msg[data_index])
                data_index += 1

            # Modify G channel
            if data_index < data_length:
                g = (g & 0b11111110) | int(msg[data_index])
                data_index += 1

            # Modify B channel
            if data_index < data_length:
                b = (b & 0b11111110) | int(msg[data_index])
                data_index += 1

            pixels[x, y] = (r, g, b, a)

    img.save(f"{UPLOAD_FOLDER}/encoded.png")
def decode():
    img = Image.open(f'{UPLOAD_FOLDER}/file.png').convert("RGBA")
    pixels = img.load()

    width, height = img.size

    bits = ""

    # Extract ALL LSB bits
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]

            bits += str(r & 1)
            bits += str(g & 1)
            bits += str(b & 1)
    return binary_to_text(message_bits_from_payload(bits))



# Οι καθορισμένες κλίμακες (ranges)
RANGES = [(0, 7), (8, 15), (16, 31), (32, 63), (64, 127), (128, 255)]

def get_range(diff):
    """Επιστρέφει την κλίμακα στην οποία ανήκει η διαφορά diff."""
    abs_d = abs(diff)
    for r in RANGES:
        if r[0] <= abs_d <= r[1]:
            return r
    return None
def pvd_encode(secret_bin):

    # Άνοιγμα εικόνας και μετατροπή σε Grayscale ('L' mode)
    img = Image.open(f"{UPLOAD_FOLDER}/file.png").convert("L")

    # Το getdata() επιστρέφει ένα sequence από pixels. Το κάνουμε list για να το τροποποιήσουμε.
    pixels = list(img.getdata())

    data_idx = 0
    data_len = len(secret_bin)

    new_pixels = pixels.copy()

    # Διατρέχουμε τα pixels ανά ζεύγη
    for i in range(0, len(pixels) - 1, 2):
        if data_idx >= data_len:
            break

        p1, p2 = pixels[i], pixels[i + 1]
        d = p2 - p1
        r = get_range(d)

        if not r: continue

        l, u = r
        w = u - l + 1
        n = int(math.log2(w))  # Bits που μπορούμε να κρύψουμε

        if n == 0: continue

        bits_to_embed = secret_bin[data_idx: data_idx + n]

        if len(bits_to_embed) < n:
            bits_to_embed = bits_to_embed.ljust(n, '0')

        b = int(bits_to_embed, 2)
        d_prime = l + b

        if d < 0:
            d_prime = -d_prime

        m = abs(d_prime) - abs(d)

        # Υπολογισμός νέων τιμών
        if d >= 0:
            p1_prime = p1 - math.ceil(m / 2)
            p2_prime = p2 + math.floor(m / 2)
        else:
            p1_prime = p1 + math.ceil(m / 2)
            p2_prime = p2 - math.floor(m / 2)

        # Shift both pixels together when needed. This preserves the new
        # difference, so the decoder reads the same bits instead of drifting.
        min_value = min(p1_prime, p2_prime)
        if min_value < 0:
            p1_prime -= min_value
            p2_prime -= min_value

        max_value = max(p1_prime, p2_prime)
        if max_value > 255:
            shift = max_value - 255
            p1_prime -= shift
            p2_prime -= shift

        if not (0 <= p1_prime <= 255 and 0 <= p2_prime <= 255):
            continue

        new_pixels[i] = p1_prime
        new_pixels[i + 1] = p2_prime
        data_idx += n

    if data_idx < data_len:
        raise ValueError("Η εικόνα δεν είναι αρκετά μεγάλη για να χωρέσει όλο το μήνυμα.")

    # Δημιουργία νέας εικόνας και αποθήκευση
    stego_img = Image.new('L', img.size)
    stego_img.putdata(new_pixels)
    stego_img.save(f"{UPLOAD_FOLDER}/encoded.png") # Σώζουμε πάντα σε PNG (Lossless)

def pvd_decode():
    """
    Ανακτά το κρυμμένο κείμενο από μια εικόνα PVD μέσω της PIL.
    """
    img = Image.open(f'{UPLOAD_FOLDER}/file.png').convert("L")
    pixels = list(img.getdata())

    extracted_bits = ""

    for i in range(0, len(pixels) - 1, 2):
        p1, p2 = pixels[i], pixels[i + 1]
        d = p2 - p1
        r = get_range(d)

        if not r: continue

        l, u = r
        w = u - l + 1
        n = int(math.log2(w))

        if n == 0: continue

        b = abs(d) - l

        extracted_bits += format(b, f'0{n}b')

    try:
        return length_prefixed_binary_to_text(extracted_bits)
    except ValueError:
        return binary_to_text(message_bits_from_payload(extracted_bits))


COS_VALS = [[math.cos(((2 * x + 1) * u * math.pi) / 16.0) for u in range(8)] for x in range(8)]
C_VALS = [1.0 / math.sqrt(2.0) if i == 0 else 1.0 for i in range(8)]

def dct_8x8(block):
    """Υπολογίζει το 2D DCT ενός μπλοκ 8x8."""
    F = [[0.0] * 8 for _ in range(8)]
    for u in range(8):
        for v in range(8):
            sum_val = 0.0
            for x in range(8):
                for y in range(8):
                    sum_val += block[x][y] * COS_VALS[x][u] * COS_VALS[y][v]
            F[u][v] = 0.25 * C_VALS[u] * C_VALS[v] * sum_val
    return F

def idct_8x8(F):
    """Υπολογίζει το Αντίστροφο 2D DCT (IDCT) ενός μπλοκ 8x8."""
    f = [[0.0] * 8 for _ in range(8)]
    for x in range(8):
        for y in range(8):
            sum_val = 0.0
            for u in range(8):
                for v in range(8):
                    sum_val += C_VALS[u] * C_VALS[v] * F[u][v] * COS_VALS[x][u] * COS_VALS[y][v]
            f[x][y] = 0.25 * sum_val
    return f
def get_block(pixels, start_x, start_y, width):
    """Αποσπά ένα 8x8 μπλοκ από το μονοδιάστατο array των pixels."""
    block = [[0.0] * 8 for _ in range(8)]
    for y in range(8):
        for x in range(8):
            block[y][x] = float(pixels[(start_y + y) * width + (start_x + x)])
    return block

def set_block(pixels, block, start_x, start_y, width):
    """Τοποθετεί ένα 8x8 μπλοκ πίσω στο array των pixels με clamping 0-255."""
    for y in range(8):
        for x in range(8):
            val = round(block[y][x])
            # Προστασία από overflow/underflow (Clamping)
            val = max(0, min(255, val))
            pixels[(start_y + y) * width + (start_x + x)] = val


def dct_encode( secret_text, D=30):
    img = Image.open(f"{UPLOAD_FOLDER}/file.png").convert("L")
    w, h = img.size

    # Κόβουμε την εικόνα ώστε να είναι πολλαπλάσιο του 8
    w_adj = w - (w % 8)
    h_adj = h - (h % 8)
    img = img.crop((0, 0, w_adj, h_adj))

    pixels = list(img.getdata())

    delimiter = '1111111111111110'
    secret_bin = text_to_binary(secret_text) + delimiter
    data_idx = 0
    data_len = len(secret_bin)

    # Οι δύο συντελεστές που θα συγκρίνουμε (μεσαίες συχνότητες)
    u1, v1 = 4, 5
    u2, v2 = 5, 4

    print("Ξεκινάει η κωδικοποίηση (Αυτό μπορεί να πάρει λίγο χρόνο)...")

    # Διατρέχουμε την εικόνα ανά 8x8 μπλοκ
    for start_y in range(0, h_adj, 8):
        for start_x in range(0, w_adj, 8):
            if data_idx >= data_len:
                break

            # 1. Παίρνουμε το block και υπολογίζουμε το DCT
            block = get_block(pixels, start_x, start_y, w_adj)
            dct_coeffs = dct_8x8(block)

            # 2. Αλλαγή των συντελεστών βάσει του bit (Koch-Zhao)
            c1 = dct_coeffs[u1][v1]
            c2 = dct_coeffs[u2][v2]
            diff = c1 - c2
            bit = secret_bin[data_idx]

            if bit == '1':
                if diff < D:
                    adj = (D - diff) / 2.0 + 1.0
                    dct_coeffs[u1][v1] += adj
                    dct_coeffs[u2][v2] -= adj
            else:  # bit == '0'
                if diff > -D:
                    adj = (diff - (-D)) / 2.0 + 1.0
                    dct_coeffs[u1][v1] -= adj
                    dct_coeffs[u2][v2] += adj

            # 3. Εφαρμογή Αντίστροφου DCT (IDCT) και αποθήκευση
            new_block = idct_8x8(dct_coeffs)
            set_block(pixels, new_block, start_x, start_y, w_adj)

            data_idx += 1

        if data_idx >= data_len:
            break

    # Δημιουργία και αποθήκευση της νέας εικόνας
    stego_img = Image.new('L', (w_adj, h_adj))
    stego_img.putdata(pixels)
    stego_img.save(f"{UPLOAD_FOLDER}/encoded.png")
    print("Η κωδικοποίηση ολοκληρώθηκε! Αποθηκεύτηκε")


def dct_decode():
    img = Image.open(f'{UPLOAD_FOLDER}/file.png').convert("L")
    w, h = img.size
    pixels = list(img.getdata())

    extracted_bits = ""
    delimiter = '1111111111111110'
    u1, v1 = 4, 5
    u2, v2 = 5, 4

    print("Ξεκινάει η αποκωδικοποίηση...")

    for start_y in range(0, h, 8):
        for start_x in range(0, w, 8):

            # Παίρνουμε το block και υπολογίζουμε το DCT
            block = get_block(pixels, start_x, start_y, w)
            dct_coeffs = dct_8x8(block)

            c1 = dct_coeffs[u1][v1]
            c2 = dct_coeffs[u2][v2]

            # Συγκρίνουμε ποιος συντελεστής είναι μεγαλύτερος
            if c1 > c2:
                extracted_bits += '1'
            else:
                extracted_bits += '0'

            # Αν εντοπιστεί ο delimiter, σταματάμε
            if delimiter in extracted_bits:
                clean_bits = extracted_bits.split(delimiter)[0]
                return binary_to_text(clean_bits)

    return "Σφάλμα: Δεν βρέθηκε ο delimiter."

def cors(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response
