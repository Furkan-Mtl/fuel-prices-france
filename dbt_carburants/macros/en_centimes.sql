-- Convertit un écart de prix en euros en centimes, arrondi à 0,1 centime
{% macro en_centimes(expression) -%}
    round(({{ expression }}) * 100, 1)
{%- endmacro %}
