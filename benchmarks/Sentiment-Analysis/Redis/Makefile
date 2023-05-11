HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest

readcsv/.readcsv_action_is_deployed: readcsv/__main__.py
	cd readcsv && zip -r readcsv_action data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Redis-readcsv readcsv/readcsv_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch readcsv/.readcsv_action_is_deployed
.PHONY: readcsv_action_invoke
readcsv_action_invoke: readcsv/.readcsv_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Sentiment-Analysis-Redis-readcsv --param-file readcsv/param.json

sentiment/.sentiment_action_is_deployed: sentiment/__main__.py
	cd sentiment && zip -r sentiment_action nltk_data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Redis-sentiment sentiment/sentiment_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch sentiment/.sentiment_action_is_deployed
.PHONY: sentiment_action_invoke
sentiment_action_invoke: sentiment/.sentiment_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Sentiment-Analysis-Redis-sentiment --param-file sentiment/param.json

WritetoDB/.WritetoDB_action_is_deployed: WritetoDB/__main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Redis-WritetoDB WritetoDB/__main__.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch WritetoDB/.WritetoDB_action_is_deployed
.PHONY: WritetoDB_action_invoke
WritetoDB_action_invoke: WritetoDB/.WritetoDB_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Sentiment-Analysis-Redis-WritetoDB --param-file WritetoDB/param.json

publishsns/.publishsns_action_is_deployed: publishsns/__main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Redis-publishsns publishsns/__main__.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch publishsns/.publishsns_action_is_deployed
.PHONY: publishsns_action_invoke
publishsns_action_invoke: publishsns/.publishsns_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Sentiment-Analysis-Redis-publishsns --param-file publishsns/param.json



.sequence_action_is_deployed: readcsv/.readcsv_action_is_deployed sentiment/.sentiment_action_is_deployed WritetoDB/.WritetoDB_action_is_deployed publishsns/.publishsns_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Sentiment-Analysis-Redis-sequence --sequence Sentiment-Analysis-Redis-readcsv,Sentiment-Analysis-Redis-sentiment,Sentiment-Analysis-Redis-WritetoDB,Sentiment-Analysis-Redis-publishsns
	touch .sequence_action_is_deployed

sequence_action_invoke: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Sentiment-Analysis-Redis-sequence --param-file readcsv/param.json

clean:
	rm -rf .sequence_action_is_deployed readcsv/.readcsv_action_is_deployed publishsns/.publishsns_action_is_deployed sentiment/.sentiment_action_is_deployed WritetoDB/.WritetoDB_action_is_deployed
	rm -rf sentiment/sentiment_action.zip readcsv/readcsv_action.zip
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Redis-sequence
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Redis-sentiment
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Redis-WritetoDB
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Redis-publishsns
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Sentiment-Analysis-Redis-readcsv
