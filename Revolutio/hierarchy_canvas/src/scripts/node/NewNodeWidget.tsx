import * as React from 'react';
import * as _ from 'lodash';
import { DiagramEngine } from '@projectstorm/react-diagrams-core';
import { NewNodeModel } from './NewNodeModel';
import { DefaultPortLabel } from '@projectstorm/react-diagrams';
import styled from '@emotion/styled';

namespace S {
	export const Node = styled.div<{ background: string; selected: boolean }>`
		background-color: ${(p) => p.background};
		border-radius: 5px;
		font-family: Arial;
		color: #495057;
		border: solid 2px rgb(255, 255, 255);
		overflow: visible;
		font-size: 11px;
		border: solid 2px ${(p) => (p.selected ? 'rgb(181, 141, 43)' : 'rgba(0,0,0,0.5)')};
	`;

	export const Title = styled.div`
		background: rgba(0,0,0,0.5);
		display: flex;
		white-space: nowrap;
		justify-items: center;
		color: white;
	`;

	export const TitleName = styled.div`
		flex-grow: 1;
		padding: 5px 5px;
		color: #fff;
	`;

	export const Ports = styled.div`
		display: flex;
	`;

	export const PortsContainer = styled.div`
		flex-grow: 1;
		display: flex;
		flex-direction: column;

		&:first-of-type {
			margin-right: 10px;
		}

		&:only-child {
			margin-right: 0px;
		}
	`;
}

export interface NewNodeProps {
	node: NewNodeModel;
	engine: DiagramEngine;
}

/**
 * Default node that models the DefaultNodeModel. It creates two columns
 * for both all the input ports on the left, and the output ports on the right.
 */
export class NewNodeWidget extends React.Component<NewNodeProps> {
	generatePort = (port) => {
		return <DefaultPortLabel engine={this.props.engine} port={port} key={port.getID()} />;
	};

	render() {
		return (
			<S.Node
				data-default-node-name={this.props.node.getOptions().name}
				selected={this.props.node.isSelected()}
				background={this.props.node.getOptions().color}>
				<S.Title>
					<S.TitleName>{this.props.node.getOptions().name}</S.TitleName>
				</S.Title>
				<S.Ports>
					<S.PortsContainer>{_.map(this.props.node.getInPorts(), this.generatePort)}</S.PortsContainer>
					<S.PortsContainer>{_.map(this.props.node.getOutPorts(), this.generatePort)}</S.PortsContainer>
				</S.Ports>
			</S.Node>
		);
	}
}
