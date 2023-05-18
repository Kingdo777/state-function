HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops
FAASTLANE_PROJECT_HOME ?= $(HOME_DIR)/PycharmProjects/faastlane
FAASTLANE_WORK_DIR ?= $(CURDIR)/.faastlane

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest

################################################################################################################################################
################################################################################################################################################
# For Faastlane

Faastlane_ACTION_NAME = Sentiment-Analysis-Faastlane

BUILD_MODE ?= PURE_PYTHON_FILE
ifeq ("$(BUILD_MODE)","PURE_PYTHON_FILE")
	ACTION_ZIP = Sentiment-Analysis.zip
else
	ACTION_ZIP = Sentiment-Analysis-Virtualenv.zip
endif

__main__.py: sentiment.py WritetoDB.py readcsv.py publishsns.py workflow.json
	FAASTLANE_WORK_DIR=$(FAASTLANE_WORK_DIR) python3 $(FAASTLANE_PROJECT_HOME)/composer/generator.py --input . --platform ow
	cp $(FAASTLANE_WORK_DIR)/__main__.py __main__.py
.PHONY: generate-faastlane-runner
generate-faastlane-runner: __main__.py

virtualenv: __main__.py nltk_data data requirements.txt
	docker run --rm -v ".:/src" --entrypoint bash $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) \
      -c "mkdir /ttt /tt && cp -r /src/* /ttt && compile main /ttt /tt && mv /tt/virtualenv /src/ && exit"
.PHONY: create-virtualenv
create-virtualenv: virtualenv

Sentiment-Analysis-Virtualenv.zip:
	zip -r Sentiment-Analysis virtualenv requirements.txt nltk_data data __main__.py readcsv.py sentiment.py WritetoDB.py publishsns.py
.PHONY: pack-virtualenv-action
pack-virtualenv-action: Sentiment-Analysis-Virtualenv.zip

Sentiment-Analysis.zip: __main__.py nltk_data data
	zip -r Sentiment-Analysis nltk_data data __main__.py readcsv.py sentiment.py WritetoDB.py publishsns.py
.PHONY: pack-action
pack-action: Sentiment-Analysis.zip

.action_is_newest: $(ACTION_ZIP)
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(Faastlane_ACTION_NAME) $(ACTION_ZIP) \
		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .action_is_newest

action_invoke_Faastlane: .action_is_newest
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result $(Faastlane_ACTION_NAME) --param op FT

################################################################################################################################################
################################################################################################################################################
# For OFC, Openwhisk, ChestBox

.readcsv_action_is_deployed: readcsv.py
	cp readcsv.py __main__.py && zip -r readcsv_action data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Three-readcsv readcsv_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .readcsv_action_is_deployed

.sentiment_action_is_deployed: sentiment.py
	cp sentiment.py __main__.py && zip -r sentiment_action nltk_data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Three-sentiment sentiment_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .sentiment_action_is_deployed

.WritetoDB_action_is_deployed: WritetoDB.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Three-WritetoDB WritetoDB.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .WritetoDB_action_is_deployed

.publishsns_action_is_deployed: publishsns.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Three-publishsns publishsns.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .publishsns_action_is_deployed

.sequence_action_is_deployed: .readcsv_action_is_deployed .sentiment_action_is_deployed .WritetoDB_action_is_deployed .publishsns_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Three-sequence --sequence Sentiment-Analysis-Three-readcsv,Sentiment-Analysis-Three-sentiment,Sentiment-Analysis-Three-WritetoDB,Sentiment-Analysis-Three-publishsns
	touch .sequence_action_is_deployed

action_invoke_OFC: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result  Sentiment-Analysis-Three-sequence --param op OFC

action_invoke_Faastorage: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result  Sentiment-Analysis-Three-sequence --param op CB

action_invoke_Openwhisk: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result  Sentiment-Analysis-Three-sequence --param op OW

clean:
	rm -rf .sequence_action_is_deployed .readcsv_action_is_deployed .publishsns_action_is_deployed .sentiment_action_is_deployed .WritetoDB_action_is_deployed __main__.py .action_is_newest
	rm -rf sentiment_action.zip readcsv_action.zip $(ACTION_ZIP)
	rm -rf .faastlane
	# rm -rf result-*
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete $(Faastlane_ACTION_NAME)
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Three-sequence
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Three-sentiment
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Three-WritetoDB
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Three-publishsns
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Three-readcsv
#	sudo rm -rf virtualenv

