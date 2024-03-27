import * as SRD from '@projectstorm/react-diagrams';
import Swal from 'sweetalert2'
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

						if (isNaN(e.link.getSourcePort().getOptions().name)) {
							var name = e.link.getSourcePort().getOptions().name
						} else {
							var name = e.link.getTargetPort().getOptions().name
						}

						var url = String(window.location.href);
						url = url.replace("DataManagement/", "api/relationship/");

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
								'parent_table': e.link.getSourcePort().getParent().getOptions().name,
								'child_table': e.link.getTargetPort().getParent().getOptions().name,
								'child_element': name,
							})
						})
						.then(data => {
							console.log(data.body)
							if (data.body.status == 201) {
								Swal.fire({icon: 'success',text: 'Relationship created successfully!'});
							} else {
								Swal.fire({icon: 'error',text: data.body.message});
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
