Om ni gör ändringar - gör på en ny branch och öppna en pull request, det går inte att pusha direkt till main


## Terminalversion

Kör med Python 3.12 eller senare:

```sh
python blackjack.py
```

Varje spelare anger ett positivt heltal som startsaldo och satsar före utdelningen.
Insatsen får inte överstiga saldot. Spelarna jämförs var för sig med dealern.
Vanlig vinst betalar 1:1, blackjack betalar 3:2 och oavgjort ger insatsen tillbaka.
Blackjack kräver två kort. Dealern stannar på alla 17, även mjuk 17.
Om kortleken tar slut avbryts rundan och alla insatser återbetalas.
Spelare med mindre än 1 kvar deltar inte i nästa runda. Efter rundan kan du avsluta.

Kör regressionstesterna:

```sh
python -B -m unittest -v test_blackjack
```

`blackjack_gui.py` är en separat, ofärdig version. Den har sedan tidigare
ogiltiga `lazy import`-satser och använder både `bank` och `bank_value`.
Insatsändringarna och testerna ovan gäller terminalversionen.
