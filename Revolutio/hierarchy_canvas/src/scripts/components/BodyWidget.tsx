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
import Modal from 'react-bootstrap/Modal'
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form'
import Col from 'react-bootstrap/Col';
import CreatableSelect from 'react-select/creatable';
import Select from 'react-select';
import Swal from 'sweetalert2';
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


interface Option {
	readonly label: string;
	readonly value: string;
  }

  const style = {
    control: (base, state) => ({
      ...base,
      borderColor: state.isFocused ? "var(--primary-color)" : "lightgrey",
	  boxShadow: state.isFocused ? 0 : 0,
      "&:hover": {
        borderColor: state.isFocused ? "var(--primary-color)" : "lightgrey"
      }
    })
  };


export class BodyWidget extends React.Component<BodyWidgetProps> {

	engine: DagreEngine;

	constructor(props) {
		super(props);
		this.state = {
		  data: [],
		  loaded: "false",
		  placeholder: "Loading",
		  filteredData: [],
		  gridlines: true,
		  gridcolor: "rgba(60,60,60, 0.05)",
		  modalShow: false,
		  group: [],
		  parent_list: [],
		  hierarchy_type_list: [],
		  hierarchy_group_list: [],
		  hierarchy_level_name_list: [],
		  hierarchy_description_list: [],
		  loaded_group: false,
		  loaded_parent: false,
		  placeholder_group: "Loading",
		  selectedFile: null
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

	componentDidMount() {
		var dhParentNameURL = String(window.location.href);
		dhParentNameURL = dhParentNameURL.replace(`DataManagement/`, `api/hierarchy_data/`);

		fetch(dhParentNameURL)
		.then(response => {
			return response.json();
		})
		.then(data => {
			var hierarchy_type = [];
			var hierarchy_parent_list = [];
			var hierarchy_group = [];
			var hierarchy_level_name = [];
			var hierarchy_description = [];
			data.hierarchy_type.forEach(par => {
				hierarchy_type.push(this.createOption(par));
			});
			data.hierarchy_group.forEach(par => {
				hierarchy_group.push(this.createOption(par));
			});
			data.hierarchy_level_name.forEach(par => {
				hierarchy_level_name.push(this.createOption(par));
			});
			data.hierarchy_description.forEach(par => {
				hierarchy_description.push(this.createOption(par));
			});
			data.hierarchy_name.forEach(par => {
				hierarchy_parent_list.push(this.createOption(par));
			});
			this.setState(() => {
				return {
					parent_list: hierarchy_parent_list,
					hierarchy_type_list: hierarchy_type,
					hierarchy_group_list: hierarchy_group,
					hierarchy_level_name_list: hierarchy_level_name,
					hierarchy_description_list: hierarchy_description,
					loaded_parent: true,
				};
			});
		});
	}

	getApidata = () => {
		var url = String(window.location.href);
		url = url.replace(`DataManagement/`, "api/hierarchy_level_info/");
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

		var url2 = String(window.location.href);
		url2 = url2.replace(`DataManagement/`, `api/hierarchy_group/`);

		fetch(url2)
		.then(response => {
			return response.json();
		})
		.then(data => {
			this.setState(() => {
				return {
					group: data,
					loaded_group: true,
					placeholder: "Loaded",
				};
			});
		});

		var url2 = String(window.location.href);
		url2 = url2.replace(`DataManagement/`, "api/hierarchy_group/");

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

	handleShow = () => {
		this.setState(() => {
			return {
				modalShow: true
			}
		})
	};

	handleClose = () => {
		this.setState(() => {
			return {
				modalShow: false
			}
		})
	};

	formsubmit = (event) => {

		event.preventDefault()

		let form = event.target
		var type = form.elements.type.value
		var group = form.elements.group.value
		var name = form.elements.name.value
		var parent_name = form.elements.parent_name.value
		var level = form.elements.level.value
		var level_name = form.elements.level_name.value
		var description = form.elements.description.value
		var configuration_date = form.elements.configuration_date.value

		var url = String(window.location.href);
		url = url.replace(`DataManagement/`, "api/hierarchy/");

		const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

		fetch(url, {
			credentials: 'include',
			method:"POST",
			headers:{
			  'Accept':'application/json',
			  'Content-Type': 'application/json',
			  'X-CSRFToken': csrftoken,
			},
			body: JSON.stringify({
				'hierarchy_type': type,
				'hierarchy_group': group,
				'hierarchy_name': name,
				'hierarchy_parent_name': parent_name,
				'hierarchy_level': level,
				'hierarchy_level_name': level_name,
				'hierarchy_description': description,
				'configuration_date': configuration_date,
			})
		})
		.then(response => {
			return response.json();
		})
		.then(data => {
			if (data.status == 201) {
				Swal.fire({icon: 'success',text: 'Hierarchy created successfully!'});
			} else {
				Swal.fire({icon: 'warning',text:`Please fill in the values for the following fields: ${JSON.stringify(data.mandatory_fields)}.`});
			}
		});
	}

	getHierarchyLevel = e => {
		var dhLevelInfoURL = String(window.location.href);
		dhLevelInfoURL = dhLevelInfoURL.replace(`DataManagement/`, "api/hierarchy_level_info/");
		var parent_name = e.value
		const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

		fetch(dhLevelInfoURL, {
			credentials: 'include',
			method:"POST",
			headers:{
			  'Accept':'application/json',
			  'Content-Type': 'application/json',
			  'X-CSRFToken': csrftoken,
			},
			body: JSON.stringify({
				'operation': "fetch_hierarchy_level",
				'parent_name': parent_name,
			})
		})
		.then(response => {
			return response.json();
		})
		.then(data => {
			document.getElementById("dh_hierarchy_level").value = data.level;
		});
	}

	createOption = (label: string) => ({
		label,
		value: label,
	});

	handleCreateHT = (inputValue: string) => {
		setTimeout(() => {
		  const options = this.state.hierarchy_type_list;
		  const newOption = this.createOption(inputValue);
		  this.setState({
			hierarchy_type_list: [...options, newOption],
		  });
		}, 100);
	};

	handleCreateHG = (inputValue: string) => {
		setTimeout(() => {
		  const options = this.state.hierarchy_group_list;
		  const newOption = this.createOption(inputValue);
		  this.setState({
			hierarchy_group_list: [...options, newOption],
		  });
		}, 100);
	};

	handleCreateHLN = (inputValue: string) => {
		setTimeout(() => {
		  const options = this.state.hierarchy_level_name_list;
		  const newOption = this.createOption(inputValue);
		  this.setState({
			hierarchy_level_name_list: [...options, newOption],
		  });
		}, 100);
	};

	handleCreateHD = (inputValue: string) => {
		setTimeout(() => {
		  const options = this.state.hierarchy_description_list;
		  const newOption = this.createOption(inputValue);
		  this.setState({
			hierarchy_description_list: [...options, newOption],
		  });
		}, 100);
	};

	optionSelect = () => {
		return <option>XYUBUN</option>
	};

	__handleLevelSelection = () => {
		document.getElementById("selectHierarchyLevelName").onchange = (e) => {
			if (e.target.value) {
				var hierarchyGroup = document.getElementById("selectHierarchyGroup").value
				var node = new NewNodeModel(hierarchyGroup, 'rgb(255, 255, 255)')
				node.setPosition(50, 50)
				node.addOutPort(e.target.value, false)
				this.props.app.getDiagramEngine().getModel().addNode(node)
				this.forceUpdate();
			}
		}
	}

	uploadFileChange = (e) => {
		this.setState({ selectedFile: e.target.files[0] });
	}

	uploadFileUpload = (e) => {
		e.preventDefault();

		// Create an object of formData
		const formData = new FormData();

		// Update the formData object
		formData.append('upload', this.state.selectedFile);
		formData.append('name', this.state.selectedFile.name);
		formData.append("operation", "uploadHierarchy");

		// Details of the uploaded file
		var dhLevelInfoURL = String(window.location.href);
		dhLevelInfoURL = dhLevelInfoURL.replace(`DataManagement/`, "api/hierarchy_uploads/");
		var parent_name = e.value
		const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

		fetch(dhLevelInfoURL, {
			credentials: 'include',
			method:"POST",
			headers:{
			  'X-CSRFToken': csrftoken,
			},
			body: formData,
		})
		.then(response => {
			return response.json();
		})
		.then(data => {
			if(data["status"] != 201){
				Swal.fire({icon: 'warning',text:data["message"]});
			} else {
				Swal.fire({icon: 'success',text: 'Upload successful!'});
			}
		});

		// Request made to the backend api
		// Send formData object
	}

	downloadFile = (e) => {
		e.preventDefault();
		var csvFileData = [
			['', '','','','','','']
		  ];
		  //define the heading for each row of the data
		  var csv = 'hierarchy_type,hierarchy_group,hierarchy_name,hierarchy_parent_name,hierarchy_level_name,hierarchy_description,configuration_date\n';

		  //merge the data with CSV
		  csvFileData.forEach(function(row) {
				  csv += row.join(',');
				  csv += "\n";
		  });
		  var hiddenElement = document.createElement('a');
		  hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
		  hiddenElement.target = '_blank';
		  hiddenElement.download = 'data.csv';
		  hiddenElement.click();
	}

	render() {

		this.props.app.getDiagramEngine().getNodeFactories().registerFactory(new NewNodeFactory());

		var elements=[];
        for(var i=0;i<this.state.filteredData.length;i++){
			// push the component to elements!
			var columns=this.state.filteredData[i].fields.toString();
			elements.push(<TrayItemWidget name={this.state.filteredData[i].tablename} tooltip={columns.replaceAll(',','<br />')} />)
		}
		setTimeout(() => {
			this.__handleLevelSelection();
		}, 250);

		return (
			<DemoWorkspaceWidget
				buttons={[
					<DemoButton key={1} onClick={this.autoDistribute}>Re-distribute</DemoButton>,
					<DemoButton key={2} onClick={this.changegridlines}>Grid Lines</DemoButton>,
					<DemoButton key={3} variant="primary" onClick={this.handleShow}>
						Create hierarchy
				  	</DemoButton>,
					<DemoButton key={4} onClick={this.getApidata}>Fetch Data</DemoButton>,
				]}>

				<Modal
					size="lg"
					aria-labelledby="contained-modal-title-vcenter"
					show={this.state.modalShow}
					keyboard={false}
				>
					<Form onSubmit={(e) => this.formsubmit(e)}>
						<Modal.Header closeButton onHide={this.handleClose}>
							<Modal.Title id="contained-modal-title-vcenter">
								Create new hierarchy
							</Modal.Title>
						</Modal.Header>
						<Modal.Body>
							<div className='card'>
								<div className='card-header'>
								<h6 class="card-title">Create hierarchy by upload</h6>
								</div>
								<div className='card-body'>
									<Form.Row>
										<div className='row mt-4 ml-1'>
											<input type="file" name="upload" onChange={this.uploadFileChange}/>

											<button className='btn-primary fa fa-upload' data-toggle="tooltip" title="Upload hierachy" onClick={this.uploadFileUpload}>
											</button>
											<button className='btn-primary fa fa-download' data-toggle="tooltip" title="Download format" onClick={this.downloadFile}>
											</button>
										</div>
									</Form.Row>
								</div>
								<div className='card-header mt-6'>
								<h6 class="card-title">Create hierarchy by form</h6>
								</div>
								<div className='card-body'>
									<Form.Row>
										<Form.Group as={Col} controlId="dh_type">
										<Form.Label>Hierarchy type</Form.Label>
										<CreatableSelect
											required
											isClearable
											name="type"
											onCreateOption={this.handleCreateHT}
											options={this.state.hierarchy_type_list}
											styles={style}
											theme={(theme) => ({
												...theme,
												colors: {
												...theme.colors,
												primary25: 'var(--primary-color)',
												primary50: 'var(--primary-color)',
												primary75: 'var(--primary-color)',
												primary: 'var(--primary-color)',
												},
											})}
										/>
										</Form.Group>

										<Form.Group as={Col} controlId="dh_group">
										<Form.Label>Hierarchy group</Form.Label>
										<CreatableSelect
											required
											isClearable
											name="group"
											onCreateOption={this.handleCreateHG}
											options={this.state.hierarchy_group_list}
											styles={style}
											theme={(theme) => ({
												...theme,
												colors: {
												...theme.colors,
												primary25: 'var(--primary-color)',
												primary50: 'var(--primary-color)',
												primary75: 'var(--primary-color)',
												primary: 'var(--primary-color)',
												},
											})}
										/>
										</Form.Group>
									</Form.Row>

									<Form.Row>
										<Form.Group as={Col} controlId="dh_name">
										<Form.Label>Hierarchy name</Form.Label>
										<Form.Control name="name" type="text" placeholder="Hierarchy name" required/>
										</Form.Group>

										<Form.Group as={Col} controlId="dh_parent_name">
										<Form.Label>Hierarchy parent name</Form.Label>
										<Select
											required
											isClearable
											id="dh_parent_name"
											name="parent_name"
											options={this.state.parent_list}
											onChange={this.getHierarchyLevel}
											styles={style}
											theme={(theme) => ({
												...theme,
												colors: {
												...theme.colors,
												primary25: 'var(--primary-color)',
												primary50: 'var(--primary-color)',
												primary75: 'var(--primary-color)',
												primary: 'var(--primary-color)',
												},
											})}
										/>
										</Form.Group>
									</Form.Row>
									<Form.Row>

										<Form.Group as={Col} controlId="dh_hierarchy_level">
										<Form.Label>Hierarchy level</Form.Label>
										<Form.Control name="level" type="text" placeholder="Hierarchy level" value="0" readOnly/>
										</Form.Group>

										<Form.Group as={Col} controlId="dh_hierarchy_level_name">
										<Form.Label>Hierarchy level name</Form.Label>
										<CreatableSelect
											isClearable
											name="level_name"
											onCreateOption={this.handleCreateHLN}
											options={this.state.hierarchy_level_name_list}
											styles={style}
											theme={(theme) => ({
												...theme,
												colors: {
												...theme.colors,
												primary25: 'var(--primary-color)',
												primary50: 'var(--primary-color)',
												primary75: 'var(--primary-color)',
												primary: 'var(--primary-color)',
												},
											})}
										/>
										</Form.Group>

									</Form.Row>
									<Form.Row>

										<Form.Group as={Col} controlId="dh_description">
										<Form.Label>Hierarchy description</Form.Label>
										<CreatableSelect
											isClearable
											name="description"
											onCreateOption={this.handleCreateHD}
											options={this.state.hierarchy_description_list}
											styles={style}
											theme={(theme) => ({
												...theme,
												colors: {
												...theme.colors,
												primary25: 'var(--primary-color)',
												primary50: 'var(--primary-color)',
												primary75: 'var(--primary-color)',
												primary: 'var(--primary-color)',
												},
											})}
										/>
										</Form.Group>

										<Form.Group as={Col} controlId="dh_configuration_date">
										<Form.Label>Hierarchy configuration date</Form.Label>
										<Form.Control name="configuration_date" type="date" placeholder="Configuration date" />
										</Form.Group>

									</Form.Row>
								</div>
							</div>
						</Modal.Body>
						<Modal.Footer>
							<Button variant="primary" type="submit"	>Create</Button>
							<Button onClick={this.handleClose}>Close</Button>
						</Modal.Footer>
					</Form>
				</Modal>

				<S.Body>

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
								var data = JSON.parse(event.dataTransfer.getData('storm-diagram-node'));

								// Creating table structure for table dropped on canvas
								var node = new NewNodeModel(data, 'rgb(255, 255, 255)');
								for(var i=0;i<this.state.data.length;i++){
									if (this.state.data[i].tablename === data) {
										var x = i
										var fields = this.state.data[x].fields
										for(var y=0;y<fields.length;y++){
											node.addInPort(`${y}`, false)
											node.addOutPort(fields[y], false)
										}
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
