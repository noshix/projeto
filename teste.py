import bot

teste = 'teste.jpeg'
matriz = bot.processarimagem(teste)

if matriz:
    bot.desenharimagem(matriz)
else:
    print("fudeu")
    
