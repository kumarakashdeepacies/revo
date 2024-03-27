import * as React from 'react';
import styled from '@emotion/styled';

export interface DemoWorkspaceWidgetProps {
	buttons?: any;
}

namespace S {
	export const Toolbar = styled.div`
		padding: 4px;
		display: flex;
		flex-shrink: 0;
	`;

	export const Title = styled.div`
		display: flex;
		flex-grow: 0;
		flex-shrink: 0;
		color: white;
		font-family: Helvetica, Arial, sans-serif;
		padding: 5px 10px;
		align-items: center;
		font-size: 14px;
	`;

	export const Content = styled.div`
		flex-grow: 1;
		height: 100%;
	`;

	export const Container = styled.div`
		background: var(--primary-color,var(--primary,rgb(181, 141, 43)));
		display: flex;
		flex-direction: column;
		height: 100%;
		border-radius: 5px;
		overflow: hidden;
	`;
}

export const DemoButton = styled.button`
	background: rgb(0, 0, 0);
	font-size: 14px;
	padding: 5px 10px;
	border: none;
	color: white;
	outline: none;
	cursor: pointer;
	margin: 2px;
	border-radius: 3px;

	&:hover {
		background: var(--primary-color);
	}
`;

export class DemoWorkspaceWidget extends React.Component<DemoWorkspaceWidgetProps> {


	constructor(props) {
		super(props);
		this.state = {
		  group: [],
		  loaded_group: false,
		};
	}

	componentDidMount() {
		var url2 = String(window.location.href);
		url2 = url2.replace(`DataManagement/`, "api/hierarchy_group/");

		fetch(url2)
		.then(response => {
			return response.json();
		})
		.then(data => {
			this.setState(() => {
				return {
					group: data,
					loaded_group: true,
				};
			});
		});
	}

	_handleGroupSelection = e => {
		var dhLevelNameURL = String(window.location.href);
		dhLevelNameURL = dhLevelNameURL.replace(`DataManagement/`, "api/hierarchy_level_info/");
		const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
		const selectedGroup = e.target.value;

		fetch(dhLevelNameURL, {
			credentials: 'include',
			method:"POST",
			headers:{
			  'Accept':'application/json',
			  'Content-Type': 'application/json',
			  'X-CSRFToken': csrftoken,
			},
			body: JSON.stringify({
				'operation': "fetch_hierarchy_level_name",
				'hierarchy_group': selectedGroup,
			})
		})
		.then(response => {
			return response.json();
		})
		.then(data => {
			var hierarchyLevelSelect = document.getElementById("selectHierarchyLevelName");
			var i, L = hierarchyLevelSelect.options.length - 1;
			for(i = L; i >= 0; i--) {
				hierarchyLevelSelect.remove(i);
			}
			var option = document.createElement("option");
			option.text = "-----";
			option.value = "";
			hierarchyLevelSelect.add(option);
			data.level_name.forEach(element => {
				var option = document.createElement("option");
				option.text = element;
				option.value = element;
				hierarchyLevelSelect.add(option);
			});
		});

	}

	onSelectFunc = () => {
		document.getElementById("selectHierarchyGroup").onchange = this._handleGroupSelection;
	}

	render() {
		setTimeout(() => {
			this.onSelectFunc()
		}, 250);
		return (
			<S.Container>
				<S.Toolbar className="row">
					<S.Title className = "col-2">
						Data hierarchy canvas
					</S.Title>
					<div className = "addHierarchy_Group col-3">
						<select className="select2" id="selectHierarchyGroup">
							<option value="">Select hierarchy group</option>
							{this.state.group.map(hGroup => {
								return <option value={hGroup.hierarchy_group}>{hGroup.hierarchy_group}</option>
							})}
						</select>
					</div>
					<div className = "addHierarchy_LevelName col-3">
						<select className="select2" id="selectHierarchyLevelName">
							<option>Select hierarchy level name</option>
						</select>
					</div>
					<div className = "col-4 text-right">
						{this.props.buttons}
					</div>
				</S.Toolbar>
				<S.Content>{this.props.children}</S.Content>
			</S.Container>
		);
	}
}
