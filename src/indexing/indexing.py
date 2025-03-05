from graphrag.config.load_config import load_config
import time
from graphrag.config.resolve_path import resolve_paths
import graphrag.api as api
from graphrag.logging.types import ReporterType
from graphrag.logging.factory import create_progress_reporter


async def start_indexing(root_dir,config_filepath):
    config = load_config(root_dir, config_filepath)
    
    run_id = time.strftime("%Y%m%d-%H%M%S")
    
    resolve_paths(config, run_id)
    progress_reporter = create_progress_reporter(ReporterType.PRINT)
    await api.build_index(
        config=config,
        run_id=run_id,
        is_resume_run=False,
        memory_profile=False,
        progress_reporter=progress_reporter,
    )
    
