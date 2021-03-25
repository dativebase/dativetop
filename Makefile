export DATIVETOP_IP = 127.0.0.1
export DATIVETOP_OLD_PORT = 5679
export DATIVETOP_OLD_SRC = src/old
export DATIVETOP_DATIVE_SRC = src/dative
export DATIVETOP_DATIVE_SERVERS_REL = dist/servers.json
export DATIVETOP_DATIVE_SERVERS = ${DATIVETOP_DATIVE_SRC}/${DATIVETOP_DATIVE_SERVERS_REL}

export OLD_DB_RDBMS = sqlite
export OLD_SESSION_TYPE = file
export HERE = $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
export OLD_PERMANENT_STORE = ${HERE}/oldinstances
export OLD_DB_DIRPATH = ${OLD_PERMANENT_STORE}/dbs

export DFLT_DATIVETOP_OLD_NAME = myold
export DFLT_DATIVETOP_OLD_DIR_PATH = ${OLD_PERMANENT_STORE}/${DFLT_DATIVETOP_OLD_NAME}
export DFLT_DATIVETOP_OLD_DB_PATH = ${OLD_DB_DIRPATH}/${DFLT_DATIVETOP_OLD_NAME}.sqlite

create-old-instance-simple:
	initialize_old ${DATIVETOP_OLD_SRC}/config.ini $(OLD_NAME)

create-old-instance:  ## Create an OLD instance named OLD_NAME: create a directory structure for it, an SQLite database with tables pre-populated, and register it with Dative
	initialize_old ${DATIVETOP_OLD_SRC}/config.ini $(OLD_NAME); \
		DATIVETOP_OLD_PORT=${DATIVETOP_OLD_PORT} \
		DATIVETOP_DATIVE_SERVERS=${DATIVETOP_DATIVE_SERVERS} \
		DATIVETOP_IP=${DATIVETOP_IP} \
		python dativetop/register-old-with-dative.py create $(OLD_NAME) dativetop/config.json

destroy-old-instance:  ## Destroy OLD instance OLD_NAME's files on disk and its SQLite database and de-register it from Dative
	rm -r ${OLD_PERMANENT_STORE}/$(OLD_NAME) || true; \
	rm ${OLD_PERMANENT_STORE}/dbs/$(OLD_NAME).sqlite || true; \
		DATIVETOP_OLD_PORT=${DATIVETOP_OLD_PORT} \
		DATIVETOP_DATIVE_SERVERS=${DATIVETOP_DATIVE_SERVERS} \
		DATIVETOP_IP=${DATIVETOP_IP} \
		python dativetop/register-old-with-dative.py destroy $(OLD_NAME) dativetop/config.json

build-dative:  ## Build Dative: install NPM dependencies, compile/minify JS and reset its servers array
	cd ${DATIVETOP_DATIVE_SRC};\
		yarn;\
		grunt build;\
		echo "[]" > ${DATIVETOP_DATIVE_SERVERS_REL}

launch:  ## Launch DativeTop in development mode
	@python -m dativetop

register-old-with-dative:  ## Register the default OLD instance with Dative's list of known servers
	DATIVETOP_OLD_PORT=${DATIVETOP_OLD_PORT} \
					   DATIVETOP_DATIVE_SERVERS=${DATIVETOP_DATIVE_SERVERS} \
					   DATIVETOP_IP=${DATIVETOP_IP} \
					   python dativetop/register-old-with-dative.py create ${DFLT_DATIVETOP_OLD_NAME} dativetop/config.json

beeware-build-mac-os:  ## Build the DativeTop .app bundle for Mac OS
	DFLT_DATIVETOP_OLD_NAME=${DFLT_DATIVETOP_OLD_NAME} python setup.py macos -s

build-mac-os: bootstrap-old register-old-with-dative beeware-build-mac-os  ## Build a DativeTop .app bundle for Mac OS

dmg:  ## Build a DativeTop .dmg bundle for Mac OS
	find macOS/ | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf; \
		hdiutil create -volname DativeTop.dmg -srcfolder macOS/DativeTop.app -ov -format UDZO DativeTop.dmg

release-mac-os: build-mac-os dmg  ## Build for Mac OS and create a .dmg file

run-mac-os:  ## Build and run DativeTop .app bundle for Mac OS
	beeware run macOS

flush-dative:  # Reset Dative's known OLDs (servers)
	echo "[]" > ${DATIVETOP_DATIVE_SERVERS}

flush-old:  # Destroy the default OLD instance's SQLite database and directory structure
	mkdir -p ${OLD_DB_DIRPATH}; \
		rm -r ${DFLT_DATIVETOP_OLD_DIR_PATH} || true; \
		rm ${DFLT_DATIVETOP_OLD_DB_PATH} || true

initialize-old:  # Create the default OLD instance's SQLite database and directory structure
	initialize_old ${DATIVETOP_OLD_SRC}/config.ini ${DFLT_DATIVETOP_OLD_NAME}

flush: flush-dative flush-old  ## Delete ALL user data

bootstrap-old: flush-old initialize-old  ## Generate a new default OLD database and directory structure, deleting any previous ones

install:  ## Install all of the required dependencies
	pip install -r requirements.txt && \
		pip install -r src/old/requirements/testsqlite.txt && \
		pip install -e src/old/ && \
		pip install -e src/dativetop/server/ && \
		pip install requirements/wheels/dativetop_append_only_log_domain_model-0.0.1-py3-none-any.whl

dashboard:  ## Open tmux panes prepped to pilot DativeTop and its services
	tmux new-session \; \
		send-keys 'source venv/bin/activate' C-m \; \
		send-keys 'make launch' C-m \; \
		split-window -h \; \
		split-window -v \;

serve-dt-server:  ## Serve the DativeTop Server Pyramid process independently
	cd ${HERE}/src/dativetop/server; \
    ${HERE}/../venv3.6.5/bin/pserve --reload config.ini http_port=4676 http_host=127.0.0.1

help:  ## Print this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
