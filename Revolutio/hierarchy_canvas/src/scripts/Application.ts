import * as SRD from '@projectstorm/react-diagrams';
import Swal from 'sweetalert2';
/**
 * @author Dylan Vorster
 */
export class Application {
	protected activeModel: SRD.DiagramModel;
	protected diagramEngine: SRD.DiagramEngine;

	constructor() {
		this.diagramEngine = SRD.default();
		this.newModel();
	}

	public newModel() {
		this.activeModel = new SRD.DiagramModel();
		this.diagramEngine.setModel(this.activeModel);

		this.activeModel.registerListener({
			linksUpdated: function(e){
				// Do something here

				e.link.registerListener({
					targetPortChanged:function(event){
						//when a new link is created, this will be triggered

						var group_name = e.link.getSourcePort().getParent().getOptions().name;
						var group_level_name = e.link.getSourcePort().getOptions().name;
						var table_name = e.link.getTargetPort().getParent().getOptions().name;
						var field_index = e.link.getTargetPort().getOptions().name;

						var url = String(window.location.href);
						url = url.replace("DataManagement/", "api/add_hierarchy/");

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
								'group_name': group_name,
								'level_name': group_level_name,
								'table_name': table_name,
								'field_index': field_index,
							})
						})
						.then(data => {
							return data.json();
						})
						.then(data => {
							if (data.status == 201) {
								Swal.fire({icon: 'success',text: "Data hierarchy created successfully!"});
							} else if(data.status == 304){
								Swal.fire({icon: 'warning',text: data.field + " has a Foreign Key relatioship with " + data.table + ". Please configure your data hierarchy in the Parent Table."});
							} else {
								Swal.fire({icon: 'error',text: "Error! Failure in creating the data hierarchy. Please check the data hierarchy configuration and try again."});
							}
						});
					}
				})
			}
   	    });

	}

	public getActiveDiagram(): SRD.DiagramModel {
		return this.activeModel;
	}

	public getDiagramEngine(): SRD.DiagramEngine {
		return this.diagramEngine;
	}

}
