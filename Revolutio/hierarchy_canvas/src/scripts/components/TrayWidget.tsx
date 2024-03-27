import * as React from 'react';
import styled from '@emotion/styled';

namespace S {
	export const Tray = styled.div`
		min-width: 200px;
		background: #f4f6f9;
		flex-grow: 0;
		flex-shrink: 0;
		border-right: 1px solid rgba(0,0,0,.125);
		height:661px;
		overflow-x:scroll;
		overflow-y:scroll;
	`;
}

export class TrayWidget extends React.Component {
	render() {
		return <S.Tray>{this.props.children}</S.Tray>;
	}
}
