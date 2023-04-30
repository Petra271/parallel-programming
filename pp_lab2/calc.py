import matplotlib.pyplot as plt
import statistics as stats

plt.style.use("ggplot")


def ucinkovitost(T1, Tp, P):
    return T1 / Tp / P


def ubrzanje(P, E):
    return P * E


n1 = stats.mean([0.6145408153533936, 0.6024808883666992, 0.6186685562133789])
n2 = stats.mean([0.6279811859130859, 0.6207020282745361, 0.6251003742218018])
n3 = stats.mean([0.3286123275756836, 0.32315921783447266, 0.31644129753112793])
n4 = stats.mean([0.2328653335571289, 0.21816205978393555, 0.22028899192810059])
n5 = stats.mean([0.17162370681762695, 0.1667640209197998, 0.16979503631591797])
n6 = stats.mean([0.1369779109954834, 0.14132952690124512, 0.13325929641723633])
n7 = stats.mean([0.11316633224487305, 0.11283063888549805, 0.11939358711242676])
n8 = stats.mean([0.10151552200317383, 0.10365986824035645, 0.0914512252807617])

vrijeme = [n1, n2, n3, n4, n5, n6, n7, n8]
mjerenje = [i for i in range(1, 9)]


ucin = []
ubrz = []
for i in range(len(mjerenje)):
    ucin.append(ucinkovitost(n1, vrijeme[i], i + 1))
    ubrz.append(ucin[i] * (i + 1))

ideal = ubrz[:2]
ideal += [ubrz[1] * i for i in range(2, 8)]

plt.figure(figsize=(9, 15))
plt.subplot(211)
plt.title("Učinkovitost")
plt.plot(mjerenje, ucin, marker="s")
plt.subplot(212)
plt.title("Ubrzanje")
plt.plot(mjerenje, ubrz, marker="s", label="izmjereno")
plt.plot(mjerenje, ideal, marker="s", label="idealno")
plt.legend()
plt.show()
