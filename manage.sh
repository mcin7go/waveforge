#!/bin/bash
set -e
# Kolory dla czytelności
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # Brak koloru

# --- Główna funkcja ---
main() {
    case "$1" in
        start|up) start_containers ;;
        stop|down) stop_containers ;;
        restart) restart_containers ;;
        rebuild) rebuild_and_start ;;
        logs) show_logs "$2" ;;
        status|ps) show_status ;;
        env) show_env ;;
        test) run_tests "$2" ;;
        db:shell) db_shell ;;
        db:init) db_init ;;
        seed:users) seed_users ;;
        i18n:init) i18n_init "$2" ;;
        i18n:update) i18n_update ;;
        i18n:compile) i18n_compile ;;
        debug:sessionkey) debug_sessionkey ;;
        help|--help|-h) show_help ;;
        *) show_help ;;
    esac
}

# --- Funkcja Pomocy ---
show_help() {
    echo -e "${CYAN}=====================================================${NC}"
    echo -e "${CYAN}     Skrypt Zarządzający Projektem vaveforgepro      ${NC}"
    echo -e "${CYAN}=====================================================${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC} ./manage.sh [command]"
    echo ""
    echo -e "${CYAN}--- Szczegółowa Lista Poleceń ---${NC}"
    echo -e "  ${YELLOW}start, up${NC}           Uruchamia wszystkie kontenery w tle."
    echo -e "  ${YELLOW}stop, down${NC}          Zatrzymuje i usuwa wszystkie kontenery."
    echo -e "  ${YELLOW}restart${NC}             Zatrzymuje i ponownie uruchamia kontenery."
    echo -e "  ${YELLOW}rebuild${NC}             Przebudowuje obrazy Docker i uruchamia kontenery."
    echo -e "  ${YELLOW}logs [svc]${NC}         Śledzi logi na żywo. Opcjonalnie podaj nazwę serwisu."
    echo -e "  ${YELLOW}status, ps${NC}          Wyświetla status działających kontenerów."
    echo -e "  ${YELLOW}test [path]${NC}         Uruchamia testy Pytest. Opcjonalnie podaj ścieżkę."
    echo -e "  ${YELLOW}db:shell${NC}            Otwiera konsolę 'psql' do bazy danych."
    echo -e "  ${YELLOW}db:init${NC}             Niszczy i odtwarza bazę danych od zera."
    echo -e "  ${YELLOW}seed:users${NC}          Dodaje 10 losowych użytkowników do bazy."
    echo -e "  ${YELLOW}i18n:update${NC}         Aktualizuje pliki tłumaczeń (.po)."
    echo -e "  ${YELLOW}i18n:compile${NC}        Kompiluje pliki .po do formatu .mo."
    echo -e "  ${YELLOW}i18n:init <lang>${NC}    Tworzy nowy katalog tłumaczeń dla języka."
    echo -e "  ${YELLOW}env${NC}                 Wyświetla zmienne środowiskowe kontenera 'web'."
    echo -e "  ${YELLOW}debug:sessionkey${NC}    Sprawdza, czy SECRET_KEY jest poprawnie wczytany."
    echo -e "  ${YELLOW}help, --help, -h${NC}    Wyświetla tę wiadomość."
    echo ""
}

# --- Funkcje wykonawcze ---
start_containers() { docker-compose up -d; show_status; }
stop_containers() { docker-compose down; }
restart_containers() { stop_containers; start_containers; }
rebuild_and_start() { docker-compose up --build -d; show_status; }
show_logs() { docker-compose logs -f "$1"; }
show_status() { docker-compose ps; }
show_env() { docker-compose run --rm web env; }
run_tests() {
    if [ -z "$1" ]; then
        docker-compose exec web pytest
    else
        docker-compose exec web pytest "$1"
    fi
}
db_shell() { docker-compose exec db psql -U waveforgepro -d waveforgepro; }
db_init() {
    read -p "Are you sure? This will delete the database volume. [y/N] " -n 1 -r; echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --remove-orphans
        start_containers
        echo -e "${GREEN}Database re-initialized.${NC}"
    fi
}
seed_users() { docker-compose exec web flask seed-users; }
i18n_init() {
    if [ -z "$1" ]; then
        echo "Error: Language code is required. Example: ./manage.sh i18n:init de"; return 1;
    fi
    docker-compose exec web bash -c "pybabel extract -F babel.cfg -k _ -o messages.pot . && pybabel init -i messages.pot -d app/translations -l $1 && rm messages.pot"
}
i18n_update() {
    docker-compose exec web bash -c "pybabel extract -F babel.cfg -k _ -o messages.pot . && pybabel update -i messages.pot -d app/translations && rm messages.pot"
    echo -e "${GREEN}Catalogs updated. Please translate new strings in the .po files.${NC}"
}
i18n_compile() {
    docker-compose exec web bash -c "pybabel compile -d app/translations"
    echo -e "${GREEN}Translations compiled. Restart the app to see changes.${NC}"
}
debug_sessionkey() {
    echo -e "${YELLOW}Sprawdzanie SECRET_KEY wewnątrz kontenera...${NC}"
    docker-compose exec web python -c "from app import create_app; app = create_app(); print(f'SECRET_KEY = \'{app.config.get('SECRET_KEY')}\'')"
}

main "$@"
