import os

import pandas as pd

from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
import dotenv
import asyncio
from .SearchEngine import SearchEngine
from .search_config import *
import threading
from graphrag.api.query import _patch_vector_store,_get_embedding_store,read_indexer_entities,read_indexer_covariates,_load_search_prompt,get_local_search_engine
from graphrag.config.load_config import load_config
from graphrag.index.config.embeddings import entity_description_embedding
from graphrag.config.resolve_path import resolve_paths
from pathlib import Path
from graphrag.vector_stores.factory import VectorStoreType

class LocalSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__()
        self.build_thread = threading.Thread(target=self.build_task,name ="LocalSearchEngineBuildThread",daemon=True)

    def build_task(self):
        try:
            self.engine_state = self.STATE_BUILDING
            # 環境変数の読み込み
            dotenv.load_dotenv("./ragdata/.env",override=True)

            config = load_config(Path("./ragdata").resolve(), Path("ragdata/settings.yaml"))
            config.storage.base_dir = str({INPUT_DIR}) if {INPUT_DIR} else config.storage.base_dir
            resolve_paths(config)

            final_nodes = pd.read_parquet(f"{INPUT_DIR}/{NODE_TABLE}.parquet")
            final_community_reports = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_REPORT_TABLE}.parquet")
            final_text_units: pd.DataFrame = pd.read_parquet(f"{INPUT_DIR}/{TEXT_UNIT_TABLE}.parquet")
            final_relationships: pd.DataFrame = pd.read_parquet(f"{INPUT_DIR}/{RELATIONSHIP_TABLE}.parquet")
            final_entities: pd.DataFrame = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")
            final_covariates: pd.DataFrame = pd.read_parquet(f"{INPUT_DIR}/{COVARIATE_TABLE}.parquet")
            
            config = _patch_vector_store(config, final_nodes, final_entities, COMMUNITY_LEVEL)
            vector_store_type = config.embeddings.vector_store.get("type")  # type: ignore
            vector_store_args = config.embeddings.vector_store
            if vector_store_type == VectorStoreType.LanceDB:
                db_uri = config.embeddings.vector_store["db_uri"]  # type: ignore
                lancedb_dir = Path(config.root_dir).resolve() / db_uri
                vector_store_args["db_uri"] = str(lancedb_dir)  # type: ignore

            description_embedding_store = _get_embedding_store(
                config_args=config.embeddings.vector_store,  # type: ignore
                embedding_name=entity_description_embedding,
            )
            entities_ = read_indexer_entities(final_nodes, final_entities, COMMUNITY_LEVEL)
            covariates_ = read_indexer_covariates(final_covariates) if final_covariates is not None else []
            prompt = _load_search_prompt(config.root_dir, config.local_search.prompt)

            self.search_engine = get_local_search_engine(
                config=config,
                reports=read_indexer_reports(final_community_reports, final_nodes, COMMUNITY_LEVEL),
                text_units=read_indexer_text_units(final_text_units),
                entities=entities_,
                relationships=read_indexer_relationships(final_relationships),
                covariates={"claims": covariates_},
                description_embedding_store=description_embedding_store,  # type: ignore
                response_type="multiple paragraphs",
                system_prompt=prompt,
            )
            self.engine_state = self.STATE_BUILD_COMPLETE
        except Exception as e:
            self.engine_state = self.STATE_BUILD_FAILED
            self.err_msg = str(e)
        

    def build(self):
        if not self.build_thread.is_alive():
            self.build_thread = threading.Thread(target=self.build_task,name ="LocalSearchEngineBuildThread",daemon=True)
            self.build_thread.start()
            
    async def build_wait(self):
        while self.build_thread.is_alive():
            await asyncio.sleep(0.1)
              
    # クエリの実行
    async def search(self,query):
        if self.engine_state != self.STATE_BUILD_COMPLETE:
            self.build()
        # engineのbuildが完了していなければ待つ
        await self.build_wait()
        
        if self.engine_state != self.STATE_BUILD_COMPLETE:
            return -1,self.err_msg
        
        try:
            result = await self.search_engine.asearch(query)
            return 0,result.response
        except Exception as e:
            return -1,str(e)
    