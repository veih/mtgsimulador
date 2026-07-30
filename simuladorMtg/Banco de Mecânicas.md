Em vez de gravar apenas texto:

Flying

você grava:

{
    "id":"FLYING",
    "type":"static",
    "zone":"battlefield",
    "description":"Can't be blocked except by creatures with flying or reach."
}

Outro exemplo

{
    "id":"FLASH",
    "type":"permission",
    "description":"You may cast this spell any time you could cast an instant."
}

Outro

{
    "id":"CASCADE",
    "type":"triggered",
    "trigger":"cast_spell",
    "effect":"cascade"
}