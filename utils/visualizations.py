import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
import pandas as pd
import networkx as nx

def create_odds_chart(market_data: Dict, historical_data: List[Dict] = None):
    """
    Create an interactive odds chart for a single market
    """
    if historical_data:
        df = pd.DataFrame(historical_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['yes_price'],
            mode='lines',
            name='Yes Price',
            line=dict(color='#10b981', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['no_price'],
            mode='lines',
            name='No Price',
            line=dict(color='#ef4444', width=2)
        ))
        
        fig.update_layout(
            title=market_data['title'],
            xaxis_title='Time',
            yaxis_title='Price',
            yaxis=dict(tickformat='.0%'),
            hovermode='x unified',
            template='plotly_dark'
        )
        
        return fig
    else:
        fig = go.Figure(data=[
            go.Bar(
                x=['Yes', 'No'],
                y=[market_data['yes_price'], market_data['no_price']],
                marker_color=['#10b981', '#ef4444']
            )
        ])
        
        fig.update_layout(
            title=market_data['title'],
            yaxis=dict(tickformat='.0%'),
            template='plotly_dark'
        )
        
        return fig

def create_network_map(markets: List[Dict]):
    """
    Create a network graph showing market correlations
    """
    G = nx.Graph()
    
    categories = list(set([m['category'] for m in markets]))
    
    for category in categories:
        G.add_node(category, node_type='category')
    
    for market in markets[:20]:
        market_id = market['id']
        G.add_node(market_id, 
                   node_type='market',
                   title=market['title'],
                   price=market['yes_price'])
        
        G.add_edge(market['category'], market_id)
    
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        )
    )
    
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        
        if G.nodes[node].get('node_type') == 'category':
            node_trace['text'] += tuple([node])
        else:
            node_trace['text'] += tuple([G.nodes[node].get('title', '')[:30]])
    
    node_adjacencies = []
    for node in G.nodes():
        node_adjacencies.append(len(list(G.neighbors(node))))
    
    node_trace.marker.color = node_adjacencies
    
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title='Market Correlation Network',
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=0, l=0, r=0, t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       template='plotly_dark'
                   ))
    
    return fig

def create_sentiment_heatmap(markets: List[Dict]):
    """
    Create a heatmap showing sentiment across categories
    """
    df = pd.DataFrame(markets)
    
    if df.empty:
        return None
    
    pivot_data = df.pivot_table(
        values='yes_price',
        index='category',
        aggfunc='mean'
    )
    
    fig = px.bar(
        pivot_data,
        orientation='h',
        title='Average Market Confidence by Category',
        labels={'value': 'Avg Yes Price', 'category': 'Category'},
        color=pivot_data.values.flatten(),
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        xaxis=dict(tickformat='.0%'),
        template='plotly_dark'
    )
    
    return fig

def create_volume_chart(markets: List[Dict]):
    """
    Create a volume comparison chart
    """
    df = pd.DataFrame(markets)
    
    if df.empty:
        return None
    
    top_markets = df.nlargest(10, 'volume')
    
    fig = px.bar(
        top_markets,
        x='volume',
        y='title',
        orientation='h',
        title='Top 10 Markets by Volume',
        color='platform',
        color_discrete_map={'Polymarket': '#8b5cf6', 'Kalshi': '#3b82f6'}
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        template='plotly_dark'
    )
    
    return fig
