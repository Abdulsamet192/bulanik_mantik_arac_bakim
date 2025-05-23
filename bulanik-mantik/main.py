import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ------------------ Fuzzy Logic Setup ------------------ #
bakim_siklik = ctrl.Antecedent(np.arange(0, 11, 1), 'bakim_siklik')
ariza_gecmisi = ctrl.Antecedent(np.arange(0, 11, 1), 'ariza_gecmisi')
kilometre = ctrl.Antecedent(np.arange(0, 301000, 1000), 'kilometre')
yas = ctrl.Antecedent(np.arange(0, 21, 1), 'yas')
tur = ctrl.Antecedent(np.arange(0, 11, 1), 'tur')

bakim_onceligi = ctrl.Consequent(np.arange(0, 101, 1), 'bakim_onceligi')
onarim_onceligi = ctrl.Consequent(np.arange(0, 101, 1), 'onarim_onceligi')

for var in [bakim_siklik, ariza_gecmisi, kilometre, yas, tur]:
    var.automf(3)

bakim_onceligi['dusuk'] = fuzz.trimf(bakim_onceligi.universe, [0, 0, 50])
bakim_onceligi['orta'] = fuzz.trimf(bakim_onceligi.universe, [30, 50, 70])
bakim_onceligi['yuksek'] = fuzz.trimf(bakim_onceligi.universe, [50, 100, 100])

onarim_onceligi['dusuk'] = fuzz.trimf(onarim_onceligi.universe, [0, 0, 40])
onarim_onceligi['orta'] = fuzz.trimf(onarim_onceligi.universe, [30, 50, 70])
onarim_onceligi['yuksek'] = fuzz.trimf(onarim_onceligi.universe, [60, 100, 100])

kurallar = [
    ctrl.Rule(bakim_siklik['poor'] | kilometre['poor'], bakim_onceligi['yuksek']),
    ctrl.Rule(ariza_gecmisi['poor'] & yas['average'], onarim_onceligi['orta']),
    ctrl.Rule(tur['good'] & yas['good'], bakim_onceligi['dusuk']),
    ctrl.Rule(kilometre['average'] & ariza_gecmisi['good'], onarim_onceligi['dusuk']),
    ctrl.Rule(bakim_siklik['average'] & tur['average'], bakim_onceligi['orta']),
    ctrl.Rule(kilometre['good'] | ariza_gecmisi['poor'], onarim_onceligi['yuksek']),
]

sistem = ctrl.ControlSystem(kurallar)
sim = ctrl.ControlSystemSimulation(sistem)

def hesapla(b, a, k, y, t):
    sim.input['bakim_siklik'] = b
    sim.input['ariza_gecmisi'] = a
    sim.input['kilometre'] = k
    sim.input['yas'] = y
    sim.input['tur'] = t
    sim.compute()
    b_deg = round(sim.output['bakim_onceligi'], 2)
    o_deg = round(sim.output['onarim_onceligi'], 2)
    return b_deg, o_deg

# ------------------ GUI Setup ------------------ #
window = tk.Tk()
window.title("Askeri Araç Bakım Periyodu Sistemi")
window.geometry("800x600")
window.configure(bg="#1b3b1b")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#1b3b1b", foreground="white", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"))

frame_inputs = tk.Frame(window, bg="#1b3b1b")
frame_inputs.pack(pady=20)

labels = ["Bakım Sıklığı (0-10)", "Arıza Geçmişi (0-10)", "Kilometre (0-300000)", "Yaş (0-20)", "Araç Türü (0-10)"]
entries = []

for i, text in enumerate(labels):
    ttk.Label(frame_inputs, text=text).grid(row=i, column=0, padx=10, pady=5, sticky='w')
    entry = ttk.Entry(frame_inputs)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries.append(entry)

label_sonuc = ttk.Label(window, text="", font=("Segoe UI", 12, "bold"))
label_sonuc.pack(pady=10)

frame_chart = tk.Frame(window, bg="#1b3b1b")
frame_chart.pack()

fig, ax = plt.subplots(figsize=(4, 3))
bar_container = ax.bar(["Bakım Önceliği", "Onarım Önceliği"], [0, 0], color=["#4caf50", "#8bc34a"])
ax.set_ylim(0, 100)
ax.set_ylabel("% Değer")
fig.tight_layout()
canvas = FigureCanvasTkAgg(fig, master=frame_chart)
canvas.draw()
canvas.get_tk_widget().pack()

def hesapla_ve_goster():
    try:
        b = float(entries[0].get())
        a = float(entries[1].get())
        k = float(entries[2].get())
        y = float(entries[3].get())
        t = float(entries[4].get())

        b_oncelik, o_oncelik = hesapla(b, a, k, y, t)
        label_sonuc.config(text=f"Bakım Önceliği: %{b_oncelik} | Onarım Önceliği: %{o_oncelik}")

        bar_container[0].set_height(b_oncelik)
        bar_container[1].set_height(o_oncelik)
        canvas.draw()

    except Exception as e:
        label_sonuc.config(text="Hata: " + str(e))

ttk.Button(window, text="HESAPLA", command=hesapla_ve_goster).pack(pady=10)

window.mainloop()
