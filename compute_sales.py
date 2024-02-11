"""Module for computing sales from JSON data.

This module provides functions to load sales data from JSON files,

calculate total sales, and generate sales reports."""
import json
import sys
import os
from datetime import datetime


def load_json_file(file_path):
    """Load a JSON file, handling common errors."""

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f'Error: File {file_path} not found.')
        return None
    except json.JSONDecodeError:
        print(f'Error: File {file_path} is not valid JSON.')
        return None


def calculate_total_sales(product_catalog, sales_records,
                          sales_file, error_messages):
    """Calculate total sales from sales records using the product catalog."""

    total_cost = 0
    for sale in sales_records:
        product_name = sale.get('Product')
        quantity = sale.get('Quantity')
        if quantity is None:
            error_messages.append(
                f"Error: Registro de venta sin"
                f"cantidad en el archivo {sales_file}: "
                f"{sale}"
            )
            continue
        product_info = next(
            (item for item in product_catalog
             if item['title'] == product_name),
            None
            )
        if not product_info:
            error_messages.append(
                f"Error: Producto '{product_name}' no encontrado"
                f"en el catálogo"
                f"en el archivo {sales_file}."
                )
            continue
        product_price = product_info.get('price')
        if product_price is None:
            error_messages.append(
                f"Error: Precio no encontrado para"
                f"el producto '{product_name}' en"
                f"el archivo {sales_file}."
                )
            continue
        total_cost += product_price * quantity
    return total_cost


def main(product_catalog_file, *sales_files):
    """Esta función realiza una operación principal."""
    start_time = datetime.now()
    product_catalog = load_json_file(product_catalog_file)
    if product_catalog is None:
        return

    error_messages = []
    total_by_file = {}

    # Procesa cada archivo de ventas y calcula los totales.
    for sales_file in sales_files:
        sales_records = load_json_file(sales_file)
        if sales_records is not None:
            total_cost = calculate_total_sales(
                product_catalog, sales_records, sales_file, error_messages
                )
            total_by_file[os.path.basename(sales_file)] = total_cost

    print("\n")  # Salto de línea después de la línea de ejecución.
    for error in error_messages:
        print(error)

    print("\n")  # Salto de línea antes de los resultados de cada archivo.
    grand_total_cost = 0

    # Prepara el archivo para escribir los resultados.
    results_path = os.path.join(os.getcwd(), 'sales_results_by_file.txt')
    with open(results_path, 'w', encoding='utf-8') as result_file:
        for sales_file, total in total_by_file.items():
            result = f"{sales_file}: {total:.2f}\n"
            print(result.strip())  # Imprime el resultado en la consola.
            result_file.write(result)  # Escribe el resultado en el archivo.
            grand_total_cost += total

        grand_total_result = (
            f"Gran Total de Costo de Ventas: "
            f"{grand_total_cost:.2f}\n"
        )
        print(grand_total_result.strip())
        result_file.write(grand_total_result)

        # Escribe y muestra el tiempo transcurrido.
        time_elapsed = datetime.now() - start_time
        time_elapsed_result = f"Tiempo transcurrido: {time_elapsed}\n"
        print(time_elapsed_result.strip())
        result_file.write(time_elapsed_result)


if __name__ == "__main__":
    # Verifica que se proporcionen los argumentos correctos al script.
    if len(sys.argv) < 3:
        print(
            "\nUso: python compute_sales.py priceCatalogue.json "
            "salesRecord1.json "
            "[salesRecord2.json ...]\n"
            )
        sys.exit(1)

    main(sys.argv[1], *sys.argv[2:])
