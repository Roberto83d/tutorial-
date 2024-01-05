from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

plik_stan_konta = 'stan_konta.txt'
plik_magazynu = 'magazyn.txt'
plik_historii = 'historia.txt'

def odczytaj_stan_konta():
    try:
        with open(plik_stan_konta, 'r') as plik:
            return plik.read().strip()
    except FileNotFoundError:
        return '0'  # Zwróć string '0' dla przypadku braku pliku

def zapisz_stan_konta(stan):
    with open(plik_stan_konta, 'w') as plik:
        plik.write(str(stan))

def odczytaj_magazyn():
    try:
        with open(plik_magazynu, 'r') as plik:
            magazyn = {}
            for linia in plik:
                produkt, ilosc = linia.strip().split(',')
                magazyn[produkt] = int(ilosc)
            return magazyn
    except FileNotFoundError:
        return {}

def zapisz_magazyn(magazyn):
    with open(plik_magazynu, 'w') as plik:
        for produkt, ilosc in magazyn.items():
            plik.write(f"{produkt},{ilosc}\n")

def odczytaj_historie():
    try:
        with open(plik_historii, 'r') as plik:
            return plik.readlines()
    except FileNotFoundError:
        return []

def dodaj_do_historii(wpisy):
    with open(plik_historii, 'a') as plik:
        plik.write(wpisy + '\n')

@app.route('/')
def index():
    stan_konta = odczytaj_stan_konta()
    magazyn = odczytaj_magazyn()
    return render_template('index.html', stan_konta=stan_konta, magazyn=magazyn)

@app.route('/zakup', methods=['POST'])
def zakup():
    try:
        produkt = request.form['produkt']
        cena = float(request.form['cena'])
        ilosc = int(request.form['ilosc'])
    except ValueError:
        return "Bledne dane"

    magazyn = odczytaj_magazyn()
    magazyn[produkt] = magazyn.get(produkt, 0) + ilosc

    zapisz_magazyn(magazyn)
    dodaj_do_historii(f"Zakupiono {ilosc} szt. {produkt} za {cena} zl/szt.")

    return redirect(url_for('index'))

@app.route('/sprzedaz', methods=['POST'])
def sprzedaz():
    try:
        produkt = request.form['produkt']
        ilosc = int(request.form['ilosc'])
    except ValueError:
        return "Bledne dane"

    magazyn = odczytaj_magazyn()
    if produkt in magazyn and magazyn[produkt] >= ilosc:
        magazyn[produkt] -= ilosc
        zapisz_magazyn(magazyn)
        dodaj_do_historii(f"Sprzedano {ilosc} szt. {produkt}")
    else:
        return "Niewystarczająca ilosc produktu w magazynie"

    return redirect(url_for('index'))

@app.route('/zmiana_stanu_konta', methods=['POST'])
def zmiana_stanu_konta():
    try:
        zmiana = float(request.form['zmiana'])
    except ValueError:
        return "Bledne dane"

    try:
        stan_konta = float(odczytaj_stan_konta())
    except ValueError:
        # Jeśli odczytanie nie jest wartością liczbową, ustaw na 0.0
        stan_konta = 0.0

    nowy_stan_konta = stan_konta + zmiana
    zapisz_stan_konta(nowy_stan_konta)
    dodaj_do_historii(f"Zmiana stanu konta o wartosc {zmiana} zl")

    return redirect(url_for('index'))

@app.route('/historia/')
def pokaz_historie():
    historia = odczytaj_historie()
    return render_template('historia.html', historia=historia)

@app.route('/historia/<start>/<koniec>')
def pokaz_fragment_historii(start, koniec):
    try:
        start_idx = int(start)
        end_idx = int(koniec)
        historia = odczytaj_historie()
        wybrana_historia = historia[start_idx:end_idx + 1]
        return render_template('historia.html', historia=wybrana_historia)
    except (ValueError, IndexError):
        return "Niepoprawny zakres indeksów. Prosze podac poprawne indeksy."

if __name__ == '__main__':
    app.run(debug=True)
