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
		color: var(--font-hover-color);
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
		background: var(--primary-color);
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
		background: #565a5e;
	}
`;

export class DemoWorkspaceWidget extends React.Component<DemoWorkspaceWidgetProps> {
	render() {
		return (
			<S.Container>
				<S.Toolbar className="row">
					<S.Title className = "col-6">
						Data relationship canvas
					</S.Title>
					<div className = "col-6 text-right">
						{this.props.buttons}
					</div>
				</S.Toolbar>
				<S.Content>{this.props.children}</S.Content>
			</S.Container>
		);
	}
}
