from django import template
register = template.Library()

# Liefert einen Wert eines Hashes für die Templates
@register.filter
def hash(h, key):
	if key in h:
		return h[key]
	return h

# Liefert einen Wert eines 2-teiligen Hashes für die Templates
@register.filter
def hash2(_1, _2):
	return _1, _2

@register.filter
def hash3(_1_2, _3):
	_1, _2 = _1_2
	key = '!'.join((_2, _3))
	return hash(_1, key)

#Liefert den Zweck einer Rolle (ist der zweite Teil des Tupels)
@register.filter
def finde(inputset, search):
	for s in inputset:
		(name, zweck) = s
		if name == search:
			return zweck
	return ('')

