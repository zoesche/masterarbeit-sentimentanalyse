export function leerZeichenEntfernen(text: string) {
  if (!text) {
    return '';
  }

  const leerzeichenAnfangFormat = /^(\s*)/;
  const leerzeichenEndeFormat = /(\s*)$/;
  return text.replace(leerzeichenAnfangFormat, '').replace(leerzeichenEndeFormat, '');
}


export function zahlFormatieren(zahl: string) {
  return zahl.replace(',', '.');
}
