from matplotlib import pyplot as plt


def pintarHistograma(lista_valores:list,rango:range):

    ejeY = lista_valores
    ejeX = list(rango)
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.bar(ejeX, ejeY)
    plt.show()

def pintarVariosHistogramas(arrayHistogramas:list,arrayTitulos:list):

    rango = list(range(24))

    for i in range(len(arrayHistogramas)):
        plt.plot(rango,arrayHistogramas[i],label=arrayTitulos[i])

    plt.legend()
    plt.show()
