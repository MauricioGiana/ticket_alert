import questionary
from check_tickets import get_report, send_report_to_email
import form_utils
from utils import get_locations

locations = get_locations()
location_names = [location["name"] for location in locations]
location_id_map = {location["id"]: location['name'] for location in locations}
location_name_map = {location["name"]: location["id"] for location in locations}

def make_consult(consults):
    try:
        report = get_report(consults)
        send_report_to_email(report)
    except Exception as e:
        print(f"Error: {str(e)}")

def get_consult_details():
    origin = questionary.select("Seleccione origen", choices=location_names).unsafe_ask()
    destination = questionary.select("Seleccione destino", choices=location_names).unsafe_ask()
    from_date = questionary.text("Desde qué fecha? (dd-MM-yyyy)").unsafe_ask()
    to_date = questionary.text("Hasta qué fecha? (dd-MM-yyyy)").unsafe_ask()
    quantity = questionary.select("Cuántos pasajes?", choices=["uno", "dos"]).unsafe_ask()

    consult = {
        "origin_id": location_name_map[origin],
        "destination_id": location_name_map[destination],
        "from_date": from_date,
        "to_date": to_date,
        "quantity": quantity
    }
    return consult

def make_new_consult():
    consults = []
    while True:
        consult = get_consult_details()
        consults.append(consult)

        action = questionary.select(
            "Cómo continuar?", 
            choices=["Enviar reporte", "Agregar otra consulta", "Guardar consulta", "Volver"]
        ).unsafe_ask()

        if action == "Enviar reporte":
            make_consult(consults)
            break
        elif action == "Agregar otra consulta":
            continue
        elif action == "Guardar consulta":
            form_utils.save_consult(consult)
            return
        elif action == "Volver":
            return
        
def get_consult_choices():
    consult_choices = ['Volver']
    saved_consults = form_utils.get_saved_consults()
    if not saved_consults:
        print("\nNo hay consultas guardadas.\n")
        questionary.text("\nPresione enter para volver\n").unsafe_ask()
        return consult_choices

    consult_choices.extend([
        questionary.Choice(
            title=f"{i+1}. {location_id_map[consult['origin_id']]} -> {location_id_map[consult['destination_id']]} | {consult['from_date']} a {consult['to_date']} | {consult['quantity']}",
            value=i
        )
        for i, consult in enumerate(saved_consults)
    ])

    return consult_choices

def view_saved_consults():
    while True:
        consult_choices = get_consult_choices()
        selection = questionary.select("Seleccione una consulta", choices=consult_choices).unsafe_ask()

        if selection == "Volver":
            break

        form_utils.delete_consult(selection)
        print("\nConsulta eliminada\n")
        continue

def main():
    try:
        while True:
            action = questionary.select(
                "Que desea hacer?",
                choices=[
                    "Nueva consulta",
                    "Enviar reporte de consultas guardadas",
                    "Ver consultas guardadas",
                    "Limpiar consultas guardadas",
                    "Salir"
                ]
            ).unsafe_ask()

            if action == "Nueva consulta":
                make_new_consult()

            elif action == "Enviar reporte de consultas guardadas":
                saved_consults = form_utils.get_saved_consults()
                if not saved_consults:
                    print("\nNo hay consultas guardadas.\n")
                    questionary.text("\nPresione enter para volver\n").unsafe_ask()
                    continue
                make_consult(saved_consults)
                break

            elif action == "Ver consultas guardadas":
                view_saved_consults()

            elif action == "Limpiar consultas guardadas":
                form_utils.clear_consults('saved')
                questionary.text("\nConsultas limpiadas\n").unsafe_ask()
                continue

            elif action == "Salir":
                print("\nNos vemos!\n")
                break

    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
        exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()