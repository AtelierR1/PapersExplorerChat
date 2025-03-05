import os

import pandas as pd

from graphrag.query.indexer_adapters import read_indexer_entities, read_indexer_reports
from graphrag.query.structured_search.global_search.search import GlobalSearch
from graphrag.config.load_config import load_config
from graphrag.api.query import read_indexer_communities,read_indexer_entities,_load_search_prompt,get_global_search_engine
from graphrag.config.resolve_path import resolve_paths
from pathlib import Path

import dotenv
import asyncio
from .search_config import *
from .SearchEngine import SearchEngine

import threading
dotenv.load_dotenv("./ragdata/.env")


class GlobalSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__()
        self.build_thread = threading.Thread(target=self.build_task,name ="GlobalSearchEngineBuildThread",daemon=True)
        
    def build_task(self):
        try:
            # 環境変数の読み込み
            dotenv.load_dotenv("./ragdata/.env",override=True)
            
            config = load_config(Path("./ragdata").resolve(), Path("ragdata/settings.yaml"))
            config.storage.base_dir = str({INPUT_DIR}) if {INPUT_DIR} else config.storage.base_dir
            resolve_paths(config)
            
            final_nodes = pd.read_parquet(f"{INPUT_DIR}/{NODE_TABLE}.parquet")
            final_community = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_TABLE}.parquet")
            final_community_reports = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_REPORT_TABLE}.parquet")
            final_entities: pd.DataFrame = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")


            communities_ = read_indexer_communities(final_community, final_nodes, final_community_reports)
            reports = read_indexer_reports(
                final_community_reports,
                final_nodes,
                community_level=COMMUNITY_LEVEL,
                dynamic_community_selection=False,
            )
            entities_ = read_indexer_entities(final_nodes, final_entities, community_level=COMMUNITY_LEVEL)
            map_prompt = _load_search_prompt(config.root_dir, config.global_search.map_prompt)
            reduce_prompt = _load_search_prompt(
                config.root_dir, config.global_search.reduce_prompt
            )
            knowledge_prompt = _load_search_prompt(
                config.root_dir, config.global_search.knowledge_prompt
            )

            
            # 検索エンジンの構築
            self.search_engine = get_global_search_engine(
                config,
                reports=reports,
                entities=entities_,
                communities=communities_,
                response_type="multiple paragraphs",
                dynamic_community_selection=False,
                map_system_prompt=map_prompt,
                reduce_system_prompt=reduce_prompt,
                general_knowledge_inclusion_prompt=knowledge_prompt,
            )
            self.engine_state = self.STATE_BUILD_COMPLETE
            
        except Exception as e:
            self.engine_state = self.STATE_BUILD_FAILED
            self.err_msg = str(e)
    
    # グローバル検索の実行
    def build(self):
        if not self.build_thread.is_alive():
            self.build_thread = threading.Thread(target=self.build_task,name ="GlobalSearchEngineBuildThread",daemon=True)
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

    
