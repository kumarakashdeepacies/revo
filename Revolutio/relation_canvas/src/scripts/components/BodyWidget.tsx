import * as React from 'react';
import * as _ from 'lodash';
import { TrayWidget } from './TrayWidget';
import { Application } from '../Application';
import { TrayItemWidget } from './TrayItemWidget';
import { NewNodeModel } from '../node/NewNodeModel';
import { NewNodeFactory } from '../node/NewNodeFactory';
import { CanvasWidget } from '@projectstorm/react-canvas-core';
import { DemoCanvasWidget } from '../helpers/DemoCanvasWidget';
import { DemoButton, DemoWorkspaceWidget } from '../helpers/DemoWorkspaceWidget';
import { DagreEngine, PathFindingLinkFactory} from '@projectstorm/react-diagrams';
import styled from '@emotion/styled';

export interface BodyWidgetProps {
	app: Application;
}

namespace S {
	export const Body = styled.div`
		flex-grow: 1;
		display: flex;
		flex-direction: column;
		min-height: 100%;
	`;

	export const Header = styled.div`
		display: flex;
		background: rgb(181, 141, 43);
		flex-grow: 0;
		flex-shrink: 0;
		color: white;
		font-family: Helvetica, Arial, sans-serif;
		padding: 10px;
		align-items: center;
		height: 35px;
	`;

	export const Content = styled.div`
		display: flex;
		flex-grow: 1;
	`;

	export const Layer = styled.div`
		position: relative;
		flex-grow: 1;
	`;

	export const Input = styled.input`
	color: #495057;
	font-family: Arial;
	padding: 5px;
	margin: 0px 10px;
	border: 1px solid rgba(0,0,0,.125);
	border-radius: 5px;
	margin-bottom: 2px;
	margin-top: 2px;
	cursor: pointer;
	width: 205px;
	`;

}

export class BodyWidget extends React.Component<BodyWidgetProps> {

	engine: DagreEngine;

	constructor(props) {
		super(props);
		this.state = {
		  data: [],
		  loaded: "false",
		  placeholder: "Loading",
		  filteredData: [],
		  tableRelationships: {},
		  gridlines: true,
		  gridcolor: "rgba(60,60,60, 0.05)"
		};
		this.engine = new DagreEngine({
			graph: {
				rankdir: 'RL',
				ranker: 'longest-path',
				marginx: 25,
				marginy: 25
			},
			includeLinks: true
		});
	}

	getApidata = () => {
		var url = String(window.location.href);
		url = url.replace(`DataManagement/`, "api/relationship_level_info/");
		const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

		if (this.state.loaded === "false") {
			this.setState(() => {
				return {
					loaded: "running",
				};
			});
		}

		fetch(url, {
			credentials: 'include',
			method:"POST",
			headers:{
			  'Accept':'application/json',
			  'Content-Type': 'application/json',
			  'X-CSRFToken': csrftoken,
			},
			body: JSON.stringify({
				'operation': "fetch_table_info",
			})
		})
		.then(response => {
			if (response.status > 400) {
					return this.setState(() => {
					return { placeholder: "Something went wrong!" };
				});
			}
			return response.json();
		})
		.then(data => {
			var data = data.data;
			this.setState(() => {
				return {
					data,
					loaded: "true",
					filteredData: data
				};
			});
		});

		setTimeout(() => {
			this.autoDistribute();
		}, 500);
	}

	autoDistribute = () => {
		this.engine.redistribute(this.props.app.getDiagramEngine().getModel());

		// only happens if pathfing is enabled (check line 25)
		this.reroute();
		this.props.app.getDiagramEngine().repaintCanvas();
	};

	reroute() {
		this.props.app.getDiagramEngine()
			.getLinkFactories()
			.getFactory<PathFindingLinkFactory>(PathFindingLinkFactory.NAME)
			.calculateRoutingMatrix();
	}

	_handleSearchChange = e => {
		const { value } = e.target;
		const lowercasedValue = value.toLowerCase();

		this.setState(prevState => {
		  const filteredData = prevState.data.filter(el =>
			el.tablename.toLowerCase().includes(lowercasedValue)
		  );

		  return { filteredData };
		});
	};

	changegridlines = (e) => {
		if (this.state.gridlines) {
			this.setState(() => {
				return {
					gridlines: false,
					gridcolor: "rgb(255, 255, 255)"
				};
			});
		} else {
			this.setState(() => {
				return {
					gridlines: true,
					gridcolor: "rgba(60,60,60, 0.05)"
				};
			});
		}
	}

	render() {

		this.props.app.getDiagramEngine().getNodeFactories().registerFactory(new NewNodeFactory());

		var elements=[];
        for(var i=0;i<this.state.filteredData.length;i++){
			// push the component to elements!
			var columns=this.state.filteredData[i].fields.toString();
			elements.push(<TrayItemWidget name={this.state.filteredData[i].tablename} tooltip={columns.replaceAll(',','<br />')} />)
	   	}
		return (
			<DemoWorkspaceWidget
				buttons={[
					<DemoButton key={1} onClick={this.autoDistribute}>Re-distribute</DemoButton>,
					<DemoButton key={2} onClick={this.changegridlines}>Grid Lines</DemoButton>,
					<DemoButton key={3} onClick={this.getApidata}>Fetch Data</DemoButton>,
				]}>
				<S.Body>
					{/* <S.Header>
						<div className="title">Data relationship canvas</div>
					</S.Header> */}
					<S.Content>
						<TrayWidget>
							<S.Input
								onChange={this._handleSearchChange} placeholder="Search"
							>
							</S.Input>
							{this.state.loaded === "true" ? elements : this.state.loaded === "false"  ? <TrayItemWidget name={''} />: <TrayItemWidget name={'Loading ...'} /> }
						</TrayWidget>
						<S.Layer
							onDrop={event => {
								// Get data for table dropped on canvas
								var tableName = JSON.parse(event.dataTransfer.getData('storm-diagram-node'));

								// Creating table structure for table dropped on canvas
								var node = new NewNodeModel(tableName, 'rgb(255, 255, 255)');
								for(var i=0;i<this.state.data.length;i++){
									if (this.state.data[i].tablename === tableName) {
										// var tableName = data;
										var x = i
										var fields = this.state.data[x].fields;
										for(var y=0;y<fields.length;y++){
											node.addInPort(`${y}`, false)
											node.addOutPort(fields[y], false)
										};
										break;
									}
								}

								// Added table structure to canvas
								var point = this.props.app.getDiagramEngine().getRelativeMousePoint(event);
								node.setPosition(point);
								this.props.app
									.getDiagramEngine()
									.getModel()
									.addNode(node);
								this.forceUpdate();

								// Creating relatioships
								const nodes: NewNodeModel[] = _.values(this.props.app.getDiagramEngine().getModel().getNodes()) as NewNodeModel[];
								node = nodes[nodes.length - 1];
								var node_names = [];
								for (let item of nodes) {
									node_names.push(item.getOptions().name)
								}

								if (!this.state.tableRelationships[tableName]) {

									var url = String(window.location.href);
									url = url.replace(`DataManagement/`, "api/relationship_level_info/");
									var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

									fetch(url, {
										credentials: 'include',
										method:"POST",
										headers:{
										'Accept':'application/json',
										'Content-Type': 'application/json',
										'X-CSRFToken': csrftoken,
										},
										body: JSON.stringify({
											'operation': "fetch_table_rel_info",
											'tables_dropped': tableName,
										})
									})
									.then(response => {
										return response.json();
									})
									.then(data => {
										var updatedData = structuredClone(this.state.tableRelationships);
										updatedData[tableName] = data.relationships;
										this.setState(() => {
											return {
												tableRelationships: updatedData
											};
										});
									}).then(() => {
										var fields = this.state.data[x].fields;
										var relationships = this.state.tableRelationships[tableName];
										var dataCopy = this.state.data;
										for(var z=0;z<relationships.length;z++){
											if (Object.keys(relationships[z]).length !== 0) {
												var fieldName = fields[z];
												const intersection = node_names.filter(element => Object.keys(relationships[z]).includes(element));
												if (intersection.length > 0) {
													var portTo = null;
													var portOut = null;
													var link1 = null;
													Object.keys(relationships[z]).map(function(keyName, keyIndex) {
														if (node_names.includes(keyName)) {
															if (relationships[z][keyName][1] === 'Parent') {
																for (let port of node.getOutPorts()) {
																	if (port.getOptions().name === fieldName) {
																		portOut = port
																	}
																}

																for (let item of nodes) {
																	if (item.getOptions().name === keyName) {
																		var node2 = item
																	}
																}

																for(var b=0;b<dataCopy.length;b++){
																	if (dataCopy[b].tablename === keyName) {
																		var parentColIndex = dataCopy[b].fields.indexOf(fieldName);
																		break;
																	} else { continue; }
																}


																for (let port of node2.getInPorts()) {
																	if (port.getOptions().name === `${parentColIndex}`) {
																		portTo = port
																	}
																}
																link1 = portTo.link(portOut);

															} else {
																for (let port of node.getInPorts()) {
																	if (port.getOptions().name === `${z}`) {
																		portTo = port
																	}
																}

																for (let item of nodes) {
																	if (item.getOptions().name === keyName) {
																		var node2 = item
																	}
																}

																for (let port of node2.getOutPorts()) {
																	if (port.getOptions().name === relationships[z][keyName][0][0]) {
																		portOut = port
																	}
																}
																link1 = portTo.link(portOut);

															}
														}
													})
													if (link1) {
														this.props.app
															.getDiagramEngine()
															.getModel()
															.addLink(link1);
														this.props.app
															.getDiagramEngine()
															.repaintCanvas();

														_.forEach(this.props.app.getDiagramEngine().getModel().getNodes(), node => {
															_.forEach(node.getPorts(), port => {
																port.reportPosition()
															});
														})
														this.forceUpdate();
													}
												}
											}
										}
									})
								} else {
									var fields = this.state.data[x].fields;
									var relationships = this.state.tableRelationships[tableName];
									var dataCopy = this.state.data;
									for(var z=0;z<relationships.length;z++){
										if (Object.keys(relationships[z]).length !== 0) {
											var fieldName = fields[z];
											const intersection = node_names.filter(element => Object.keys(relationships[z]).includes(element));
											if (intersection.length > 0) {
												var portTo = null;
												var portOut = null;
												var link1 = null;
												Object.keys(relationships[z]).map(function(keyName, keyIndex) {
													if (node_names.includes(keyName)) {
														if (relationships[z][keyName][1] === 'Parent') {
															for (let port of node.getOutPorts()) {
																if (port.getOptions().name === fieldName) {
																	portOut = port
																}
															}

															for (let item of nodes) {
																if (item.getOptions().name === keyName) {
																	var node2 = item
																}
															}

															for(var b=0;b<dataCopy.length;b++){
																if (dataCopy[b].tablename === keyName) {
																	var parentColIndex = dataCopy[b].fields.indexOf(fieldName);
																	break;
																} else { continue; }
															}


															for (let port of node2.getInPorts()) {
																if (port.getOptions().name === `${parentColIndex}`) {
																	portTo = port
																}
															}
															link1 = portTo.link(portOut);

														} else {
															for (let port of node.getInPorts()) {
																if (port.getOptions().name === `${z}`) {
																	portTo = port
																}
															}

															for (let item of nodes) {
																if (item.getOptions().name === keyName) {
																	var node2 = item
																}
															}

															for (let port of node2.getOutPorts()) {
																if (port.getOptions().name === relationships[z][keyName][0][0]) {
																	portOut = port
																}
															}
															link1 = portTo.link(portOut);

														}
													}
												})
												if (link1) {
													this.props.app
														.getDiagramEngine()
														.getModel()
														.addLink(link1);
													this.props.app
														.getDiagramEngine()
														.repaintCanvas();

													_.forEach(this.props.app.getDiagramEngine().getModel().getNodes(), node => {
														_.forEach(node.getPorts(), port => {
															port.reportPosition()
														});
													})
													this.forceUpdate();
												}
											}
										}
									}
								}

							}}
							onDragOver={event => {
								event.preventDefault();
							}}>
							<DemoCanvasWidget color={this.state.gridcolor}>
								<CanvasWidget engine={this.props.app.getDiagramEngine()} />
							</DemoCanvasWidget>
						</S.Layer>
					</S.Content>
				</S.Body>
			</DemoWorkspaceWidget>
		);
	}
}
