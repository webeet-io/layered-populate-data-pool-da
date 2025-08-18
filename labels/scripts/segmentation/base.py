from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import google.generativeai as genai
import os
import re

class DataLoader(ABC):
    """Base class for loading data from different sources"""
    
    @property
    @abstractmethod
    def query(self) -> str:
        """Return the SQL query for this data source"""
        pass
        
    def load_data(self, engine) -> pd.DataFrame:
        """Load and return raw data as DataFrame using provided engine"""
        return pd.read_sql(self.query, engine)

class FeatureProcessor(ABC):
    """Base class for processing raw data into features"""
    
    @abstractmethod
    def process_features(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Process raw data into features"""
        pass

class SegmentationStrategy(ABC):
    """Interface for segmentation approaches"""
    
    @abstractmethod
    def segment(self, features: pd.DataFrame) -> Dict[str, List[str]]:
        """Segment neighborhoods based on features"""
        pass

class BaseClusterer(ABC):
    """Base class for clustering implementations"""
    
    @abstractmethod
    def process(self, features_df: pd.DataFrame, engine=None) -> pd.DataFrame:
        """Main processing method that returns cluster labels DataFrame"""
        pass

class BaseTagger(ABC):
    """Base class for tagging implementations"""
    
    @abstractmethod
    def calculate_tags(self, engine) -> pd.DataFrame:
        """Calculate and return tags DataFrame"""
        pass

class ResultAggregator:
    """Combines results from multiple segmentation approaches"""
    
    def __init__(self):
        self.results = {}
    
    def add_result(self, name, result: Dict[str, List[str]]):
        """Add segmentation result to aggregator"""
        if name not in self.results.keys():
            self.results[name] = {}
        self.results[name].update(result)
        #self.results.append(result)
    
    def aggregate(self) -> pd.DataFrame:
        """Combine all segmentation results into final output"""
        if not self.results:
            return pd.DataFrame(columns=['table_name', 'neighborhood', 'segments'])
            
        # Convert list of dicts to DataFrame
        combined = []
        for name, result in self.results.items():
            for neighborhood, segments in result.items():
                combined.append({
                    'table_name': name,
                    'neighborhood': neighborhood,
                    'segments': ','.join(segments)
                })
        
        return pd.DataFrame(combined)

class AgentMessage:
    """Base class for agent communication messages"""
    def __init__(self, sender: str, content: dict):
        self.sender = sender
        self.content = content

class AgentInterface(ABC):
    """Base interface for agentic components"""
    
    @abstractmethod
    def receive_message(self, message: AgentMessage):
        """Handle incoming message from another agent"""
        pass
    
    @abstractmethod
    def send_message(self, recipient: str, content: dict):
        """Send message to another agent"""
        pass

class MessageBus:
    """Central communication bus for agents"""
    def __init__(self):
        self.agents = {}
    
    def register_agent(self, agent_id: str, agent: AgentInterface):
        """Register an agent with the message bus"""
        self.agents[agent_id] = agent
    
    def route_message(self, sender: str, recipient: str, content: dict):
        """Route message between agents"""
        if recipient in self.agents:
            message = AgentMessage(sender, content)
            self.agents[recipient].receive_message(message)

class GeminiSegmentationStrategy(SegmentationStrategy):
    """Base class for Gemini-powered segmentation strategies"""
    
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        api_key = self.get_api_key()
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel('gemini-2.5-flash-lite')

    def get_api_key(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found"
                "Please set GEMINI_API_KEY environment variable or update config."
            )
        return api_key

    def _normalize_tag(self, tag: str) -> str:
        """Ensure tag has exactly one # and no starting '-'"""
        tag = tag.strip().lower()
        tag = re.sub(r'^-+', '', tag)
        tag = tag.replace(" ", "-")
        tag = re.sub(r'#+', '#', tag)
        if '#' not in tag:
            tag = '#' + tag
        return tag
    
    def _get_gemini_tags(self, prompt: str) -> list:
        """Get tags from Gemini"""
        try:
            response = self.llm.generate_content(prompt)
            tags = response.text.strip().lower().split(",")
            return [self._normalize_tag(tag) for tag in tags]
        except Exception as e:
            print(f"Gemini error: {e}")
            return ["#cluster-fallback"]